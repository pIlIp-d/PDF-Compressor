
# ==================================================================
#
#   Copyright 2021 Philip Dell (https://github.com/pIlIp-d)
#   MIT Licence
#
#========================

import lib.crunch as crunch
import argparse
import os
from pdf2image import convert_from_path
from img2pdf import convert

s = os.path.sep

FOLDER_ENDING = "_pics"
COMPRESSION_MODES = {"low":600, "medium":400, "medium-high":250, "high":150, "extreme":50}

def compress(files):
    print("--Compressing via Crunch--")
    for file in files:
        compressed = file[:-4]+"-crunch.png"
        crunch.crunch(file, pngquant_path=os.path.join("lib","pngquant","pngquant.exe") , zoplfi_path=os.path.join("lib","zopfli.exe"))
        #replace with compressed file
        os.remove(file)
        os.rename(compressed, file)

def pdf2img(pdf_path,pdf_name, mode="standard"):#splits pdf into png files
    print("--spliting pdf into images--")
    folder = pdf_name+FOLDER_ENDING
    images = convert_from_path(pdf_path, poppler_path=os.path.join("lib","poppler-22.01.0","Library","bin"),dpi=COMPRESSION_MODES[mode],thread_count=4)
    i = 1
    if not os.path.isdir(folder):
        os.mkdir(folder)
    for img in images:
        img.save(os.path.join(folder, 'page_'+str(i)+'.png'), 'PNG')
        i += 1

def clean_up(dir):#removes the directory and files that were used in compression process
    print("--cleaning up--")
    for r, _, f in os.walk(dir):
    	for file in f:
            os.remove(os.path.join(r,file))
    os.removedirs(dir)

def get_image_list(folder):
    imgs = []
    for r, _, f in os.walk(folder):
    	for fname in f:
    		if not fname.endswith(".png"):
    			continue
    		imgs.append(os.path.join(r, fname))
    return imgs

def img2pdf(pdf_name,imgs,output_file):
    print("--merging compressed images into new pdf--")
    with open(pdf_name+"_smaller.pdf","wb") as f:
    	f.write(convert(imgs))

def print_stats(origin_path, result_path):
    orig = os.stat(origin_path).st_size
    res = os.stat(result_path).st_size
    print("\nCompressed File from "+ str(round(orig / 1000000,2)) + "mb to "+ str(round(res / 1000000, 2)) + "mb ("+str(round(res / orig * 100, 2))+"%)")

def main(args):
    pdf_path = args["file"]
    pdf_name = pdf_path[:-4].split(os.path.sep)[-1].replace(" ","_")
    mode = args["mode"]
    output_file = args["output_file"]
    if output_file == "default":
        output_file = pdf_name+"_smaller.pdf"
    # - Start -
    pdf2img(pdf_path, pdf_name, mode)
    imgs = get_image_list(pdf_name+FOLDER_ENDING)
    compress(imgs)
    img2pdf(pdf_name,imgs,output_file)
    clean_up(pdf_name+FOLDER_ENDING)
    print_stats(pdf_path, output_file)

if __name__ == "__main__":
    all_args = argparse.ArgumentParser(prog='PDF Compress', usage='%(prog)s [options]', description='Compresses PDFs using png compression crunch(pngquant, zopfli).')
    all_args.add_argument("-f", "--file", required=True, help="path to pdf file")
    all_args.add_argument("-m", "--mode", required=False, help="compression mode ['low', 'medium', 'standard', 'high', 'extreme']", default='extreme')
    all_args.add_argument("-o", "--output-file", required=False, help="Compressed file Output Path. Default: 'filename_smaller.pdf'", default="default")
    args = vars(all_args.parse_args())
    main(args)
