#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ==================================================================
#
#   Copyright 2021 Philip Dell (https://github.com/pIlIp-d)
#   MIT Licence
#
# ===================================================================

import multiprocessing
import os
import shutil

try:
    import pytesseract #OCR for pdf
except:
    USE_PY_TESS = False
else:
    USE_PY_TESS = True


def get_paths_from_args(args):
    # returns properly formatted and absolute path to origin and ouput file
    # path is list of origin files(without .pdf) and output_path is either folder or file
    path = [rf"{os.path.abspath(args['path'])}"]
    output_path = rf"{args['output_path']}"
    is_dir = os.path.isdir(path[0])

    if is_dir:
        if output_path[-4:] == ".pdf":
            raise ValueError("OptionError: If path is a directory the outut must be one too!")
        if output_path == "default":
            output_path = os.path.abspath(path[0])+"_compressed"
        path = get_file_list(path[0],".pdf")
    else:
        if output_path == "default":
            output_path = os.path.abspath(path[0][:-4])+"_compressed.pdf"
        elif not output_path[-4:] == ".pdf":#output is a directory
            output_path = os.path.join(os.path.abspath(output_path), path[0].split(os.path.sep)[-1])
        else:
            pass#output as in parameter
    return path, output_path, is_dir

def pdf_compressor(pdf_file, output_file):
    #print filename in yellow
    ConsoleUtility.print("--Compressing "+ get_file_string(pdf_file) +"--")

    #save size for comparison
    orig_size = os.stat(pdf_file).st_size

    #folder for temporary files(images...)
    tmp_folder = os.path.abspath((get_filename(pdf_file) + "_tmp").replace(" ","_"))+os.path.sep
    create_folder_if_not_exist(tmp_folder)

    #split pdf into images
    pdf2img(pdf_file, tmp_folder, args["mode"])

    #list of pdf pages in png format
    imgs = get_file_list(tmp_folder,".png")

    ConsoleUtility.print("--Compressing via Crunch--")
    pool = multiprocessing.Pool()
    try:
        # multithreaded compression of single images
        # parameter is function and splitted imgs list with some length counts to display progress
        pool.starmap(crunch_compress, zip(imgs, [ len(imgs) for x in range(len(imgs)) ], [ x for x in range(len(imgs)) ]))
    except KeyboardInterrupt:
        #shutil.rmtree(folder)#clean up
        pool.terminate()
        pool.join()
        quit()
    except Exception as e:
        #shutil.rmtree(folder)#clean up after failure
        raise e
    finally: # To make sure processes are closed in the end, even if errors happen
        pool.close()
        pool.join()
        ConsoleUtility.print("** - 100.00%")#final progress step

    create_folder_if_not_exist(output_file)

    # merge images/pages into new pdf and apply OCR
    img2pdf(imgs, output_file)

    # compress pdf lossless
    cpdfsqueeze(output_file)

    # discard progress if not smaller. try simple compression with cpdfsqueeze instead
    if os.stat(pdf_file).st_size < os.stat(output_file).st_size and not args["force_ocr"]:
        if not cpdfsqueeze(pdf_file, output_file):#TODO auot mode change
            shutil.copy(pdf_file,output_file)
        ConsoleUtility.print(get_error_string("No OCR created."))

    # finish up
    clean_up(tmp_folder)
    print_stats(orig_size, os.stat(output_file).st_size)
    ConsoleUtility.print("created " + get_file_string(output_file))

def main(args):
    path, output_path, is_dir = get_paths_from_args(args)
    if len(path) == 0:
        ConsoleUtility.print(get_error_string("No PDF Found!"))
        quit(-1)
    #compress either single file or all files in folder
    for pdf_file in path[args["continue"]:]:#--continue parameter
        #remove .pdf, path (only Filename)
        pdf_name = get_filename(pdf_file)
        
        output_file = os.path.abspath(output_path)
        if is_dir:
            output_file = os.path.join(output_path, pdf_name)+".pdf"
        pdf_compressor(pdf_file, output_file)



if __name__ == "__main__":
    args, args_obj = get_args()

    main(args)
