#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ==================================================================
#
#   Copyright 2021 Philip Dell (https://github.com/pIlIp-d)
#   MIT Licence
#
# ===================================================================

import argparse
import multiprocessing
import os
import shutil
import subprocess

import compressor_lib.crunch as crunch

import fitz #package name PyMuPdf

from img2pdf import convert
from PIL import Image

try:
    import pytesseract #OCR for pdf
except:
    USE_PY_TESS = False
else:
    USE_PY_TESS = True


# colors for ANSI compatible shells
RED = "\033[0;31m"
YELLOW = "\033[0;33;33m"
GREEN = "\n\033[0;32m"
END = "\033[0m"

CPDFSQUEEZE_PATH = os.path.join(os.path.dirname(__file__),"compressor_lib","cpdfsqueeze","cpdfsqueeze.exe")
PNGQUANT_PATH = os.path.join(os.path.dirname(__file__),"compressor_lib","pngquant","pngquant.exe")
ADVPNG_PATH = os.path.join(os.path.dirname(__file__),"compressor_lib","advpng","advpng.exe")

###############################
### Compress
###############################
def crunch_compress(file, length, pos):
    #file   - string
    #length - amount of files to compress in sum across all threads
    #pos    - current file pos to calculate done progress in percentage
    compressed = file[:-4]+"-crunch.png"#temporary file
    crunch.crunch(file, pngquant_path=PNGQUANT_PATH, advpng_path=ADVPNG_PATH, quiet_=True)
    #replace with compressed file
    os.remove(file)
    os.rename(compressed, file)
    print("** - {:.2f}%".format(100*pos/length))
    
def cpdfsqueeze(origin_file, output_file = None):
    if output_file is None:
        output_file = origin_file
    try:
        subprocess.check_output(CPDFSQUEEZE_PATH+" \""+origin_file+"\" \""+output_file+"\"", stderr=subprocess.STDOUT, shell=True)
        print("--Compressed output pdf with cpdfsqueeze--")
    except Exception as e:
        print(get_error_string("cpdfsqueeze failed."))
        return 0# ignore errors at this stage
    return 1

###############################
### Convert
###############################
def init_pytesseract(args):
    global USE_PY_TESS, TESSERACT_PATH, TESSDATA_PREFIX
    #pytesseract setup
    try:
        TESSERACT_PATH =  os.path.join(os.path.expanduser('~'),"AppData","Local","Programs","Tesseract-OCR","tesseract.exe")
        TESSDATA_PREFIX =  "--tessdata-dir '"+os.path.join(os.path.expanduser('~'),"AppData","Local","Programs","Tesseract-OCR","tessdata")+"'"
        if not os.path.isfile(TESSERACT_PATH):
            print(get_error_string("[ ! ] - tesseract Path not found. Install https://github.com/UB-Mannheim/tesseract/wiki or edit 'TESSERACT_PATH' to your specific tesseract.exe"))
            quit()
        pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH
    except:
        USE_PY_TESS = False
        if args["force_ocr"]:
            print("Tesseract Not Loaded, Can't create OCR. (leave option '--ocr-force' out to compresss without hocr)")
            return False
        print(get_error_string("Tesseract failed. -> no OCR on pdfs"))
    return True

def pdf2img(pdf_path, folder, mode):
    print("--splitting pdf into images--")
    #open pdf and split it into rgb-pixelmaps -> png
    doc = fitz.open(pdf_path)
    for page in doc:
        print("** - {:.2f}%".format(100*page.number/len(doc)))
        pix = page.get_pixmap(matrix=fitz.Matrix(mode, mode))
        pix.save(os.path.join(folder, 'page_%i.png' % page.number))
    print("** - 100.00%")

def img2pdf(imgs,output_file):
    #merging pngs to pdf and create OCR
    print("--merging compressed images into new pdf and creating OCR--")
    pdf = fitz.open()
    i = 0
    for img in imgs:
        print("** - {:.2f}%".format(100*i/len(imgs)))
        i += 1
        try:
            if not USE_PY_TESS:
                raise Exception("skipping tesseract")
            result =  pytesseract.image_to_pdf_or_hocr(Image.open(img), lang="deu", extension="pdf", config=TESSDATA_PREFIX)
            open(img+".pdf", "wb").write(result)
        except:#if ocr/tesseract fails
            with open(img+".pdf","wb") as f:
                f.write(convert(img))
            if USE_PY_TESS: print("OCR couldn't be processed.")
            #ignore if ocr cant be done
        pdf.insert_pdf(fitz.open(img+".pdf"))
    if not os.path.isdir(os.path.sep.join(output_file.split(os.path.sep)[:-1])) and not os.path.sep.join(output_file.split(os.path.sep)[:-1]) == "":
        print(output_file.split(os.path.sep))
        os.mkdir(os.path.sep.join(output_file.split(os.path.sep)[:-1]))
    print("** - 100.00%")
    #raises exception if no matching permissions in output folder    
    pdf.save(output_file)

###############################
### Utility 
###############################
def get_error_string(string):
    #returns string but in red for ANSI compatible shells
    return (RED + string + END)

def get_file_string(file):
    #returns string but in yellow for ANSI compatible shells
    return (YELLOW + str(file) + END)

def print_stats(orig, result):
    print(GREEN+"Compressed File from "+ str(round(orig / 1000000,2)) + "mb to "+str(round(result / 1000000, 2)) + "mb (-"+str(round(100 - (result / orig * 100), 2))+"%)"+END)

def clean_up(folder):
    #removes the directory and files that were used in compression process
    print("--cleaning up--")
    shutil.rmtree(folder)

def get_file_list(folder, ending=".png"):
    # get all the png files in temporary folder <=> all pdf pages
    files = []
    for r, _, f in os.walk(folder):
        for fname in f:
            if not fname.endswith(ending):
                continue
            files.append(os.path.join(r, fname))
    return files

def create_folder_if_not_exist(file_or_folder_path):
    if not os.path.isdir(os.path.dirname(file_or_folder_path)):
        os.mkdir(os.path.dirname(file_or_folder_path))

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
            output_path = os.path.join(os.path.abspath(output_path), path[0].split(s)[-1])
        else:
            pass#output as in parameter
    return path, output_path, is_dir

def get_filename(full_path_to_file):
    #remove .pdf, path (only Filename)
    return full_path_to_file[:-4].split(os.path.sep)[-1]

def pdf_compressor(pdf_file, output_file):
    #print filename in yellow
    print("--Compressing "+ get_file_string(pdf_file) +"--")

    #save size for comparison
    orig_size = os.stat(pdf_file).st_size

    #folder for temporary files(images...)
    tmp_folder = os.path.abspath((get_filename(pdf_file) + "_tmp").replace(" ","_"))+os.path.sep
    create_folder_if_not_exist(tmp_folder)

    #split pdf into images
    pdf2img(pdf_file, tmp_folder, args["mode"])

    #list of pdf pages in png format
    imgs = get_file_list(tmp_folder,".png")

    print("--Compressing via Crunch--")
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
        print("** - 100.00%")#final progress step

    create_folder_if_not_exist(output_file)

    # merge images/pages into new pdf and apply OCR
    img2pdf(imgs, output_file)

    # compress pdf lossless
    cpdfsqueeze(output_file)

    # discard progress if not smaller. try simple compression with cpdfsqueeze instead
    if os.stat(pdf_file).st_size < os.stat(output_file).st_size and not args["force_ocr"]:
        if not cpdfsqueeze(pdf_file, output_file):#TODO auot mode change
            shutil.copy(pdf_file,output_file)
        print(get_error_string("No OCR created."))

    # finish up
    clean_up(tmp_folder)
    print_stats(orig_size, os.stat(output_file).st_size)
    print("created " + get_file_string(output_file))

def main(args):
    path, output_path, is_dir = get_paths_from_args(args)
    if len(path) == 0:
        print(get_error_string("No PDF Found!"))
        quit(-1)
    #compress either single file or all files in folder
    for pdf_file in path[args["continue"]:]:#--continue parameter
        #remove .pdf, path (only Filename)
        pdf_name = get_filename(pdf_file)
        
        output_file = os.path.abspath(output_path)
        if is_dir:
            output_file = os.path.join(output_path, pdf_name)+".pdf"
        pdf_compressor(pdf_file, output_file)
       

def get_args():
    all_args = argparse.ArgumentParser(prog='PDF Compress', usage='%(prog)s [options]', description='Compresses PDFs using lossy png and lossless PDF compression. Optimized for GoodNotes')
    all_args.add_argument("-p", "--path", required=True, help="Path to pdf file or to folder containing pdf files")
    all_args.add_argument("-m", "--mode", required=False, type=int, help="compression mode 1-10. 1:high 10:low compression. Default=3", default=3)
    all_args.add_argument("-o", "--output-path", required=False, help="Compressed file Output Path. Default: 'filename_smaller.pdf' or 'compressed/...' for folders", default="default")
    all_args.add_argument("-s", "--force-ocr", required=False, action='store_true', help="When turned on allows output file to be larger than input file, to force ocr. Default: off and only smaller output files are saved.'")
    all_args.add_argument("-n", "--no-ocr", required=False, action='store_true', help="Don't create OCR on pdf.")
    all_args.add_argument("-c", "--continue", required=False, type=int, help="Number. When compressing folder and Interrupted, skip files already converted. (=amount of files already converted)", default=0)
    args = vars(all_args.parse_args())
    if args["continue"] < 0:
        print("option -c --continue must be greater than or equals to 0")
        exit(-1)
    return args, all_args

if __name__ == "__main__":
    args, args_obj = get_args()
    if USE_PY_TESS:

        if args["no_ocr"]:# switch off OCR
            USE_PY_TESS = False
        elif not init_pytesseract(args):
            args_obj.print_help()
    else:
        print(get_error_string("No Module pytesseract Found. (Skipping OCR)"))
    main(args)
