
# ==================================================================
#
#   Copyright 2021 Philip Dell (https://github.com/pIlIp-d)
#   MIT Licence
#
#===================================================================

import os, argparse, subprocess, shutil
import compressor_lib.crunch as crunch
import multiprocessing
from img2pdf import convert

from datetime import datetime
import fitz #package name PyMuPdf

USE_PY_TESS = True
try:
    import pytesseract#OCR for pdf
except:
    USE_PY_TESS = False
    print("\033[0;31mNo Module pytesseract Found. (Skipping OCR)\033[00m")



s = os.path.sep
CPDFSQUEEZE_PATH = os.path.join(os.path.dirname(__file__),"compressor_lib","cpdfsqueeze","cpdfsqueeze.exe")
PNGQUANT_PATH = os.path.join(os.path.dirname(__file__),"compressor_lib","pngquant","pngquant.exe")
ADVPNG_PATH = os.path.join(os.path.dirname(__file__),"compressor_lib","advpng","advpng.exe")

FOLDER_ENDING = "_tmp"#appendix for temporary folder

def init_pytesseract(args):
    global USE_PY_TESS, TESSERACT_PATH, TESSDATA_PREFIX
    #pytesseract setup
    try:
        TESSERACT_PATH =  os.path.join(os.path.expanduser('~'),"AppData","Local","Programs","Tesseract-OCR","tesseract.exe")
        TESSDATA_PREFIX =  "--tessdata-dir '"+os.path.join(os.path.expanduser('~'),"AppData","Local","Programs","Tesseract-OCR","tessdata")+"'"
        if not os.path.isfile(TESSERACT_PATH):
            print("[ ! ] - tesseract Path not found. Install https://github.com/UB-Mannheim/tesseract/wiki or edit 'TESSERACT_PATH' to your specific tesseract.exe")
            quit()
        pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH
    except:
        USE_PY_TESS = False
        if args["force_ocr"]:
            print("Tesseract Not Loaded, Can't create OCR. (leave option '--ocr-force' out to compresss without hocr)")
            return False
        print("\033[0;31mTesseract failed. -> no OCR on pdfs\033[00m")
    return True

def pdf2img(pdf_path,pdf_name,folder, mode):
    print("--splitting pdf into images--")
    #open pdf and split it into rgb-pixelmaps -> png
    doc = fitz.open(pdf_path)
    for page in doc:
        print("** - {:.2f}%".format(100*page.number/len(doc)))
        pix = page.get_pixmap(matrix=fitz.Matrix(mode, mode))
        pix.save(os.path.join(folder, 'page_%i.png' % page.number))
    print("** - 100%")

def compress(file, length, pos):
    print("** - {:.2f}%".format(100*pos/length))
    #file = file.replace("[", "\[").replace("]", "\]").replace("(", "\(").replace(")", "\)").replace("{", "\{").replace("}", "\}")
    compressed = file[:-4]+"-crunch.png"#temporary file
    crunch.crunch(file, pngquant_path=PNGQUANT_PATH, advpng_path=ADVPNG_PATH, quiet_=True)
    #replace with compressed file
    os.remove(file)
    os.rename(compressed, file)

def get_file_list(folder, ending=".png"):# get all the png files in temporary folder <=> all pdf pages
    files = []
    for r, _, f in os.walk(folder):
        for fname in f:
            if not fname.endswith(ending):
                continue
            files.append(os.path.join(r, fname))
    return files

def img2pdf(pdf_name,imgs,output_file):#merging pngs to pdf and create OCR
    print("--merging compressed images into new pdf and creating OCR--")
    pdf = fitz.open()
    i = 0
    from PIL import Image
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
    if not os.path.isdir(s.join(output_file.split(s)[:-1])) and not s.join(output_file.split(s)[:-1]) == "":
        print(output_file.split(s))
        os.mkdir(s.join(output_file.split(s)[:-1]))
    print("** - 100%")
    pdf.save(output_file)#raises exception if no matching permissions in output folder
        

def cpdfsqueeze(origin_file, output_file = None):
    if output_file is None:
        output_file = origin_file
    try:
        subprocess.check_output(CPDFSQUEEZE_PATH+" \""+origin_file+"\" \""+output_file+"\"", stderr=subprocess.STDOUT, shell=True)
        print("--Compressed output pdf with cpdfsqueeze--")
    except Exception as e:
        print("\033[0;31mcpdfsqueeze failed.\033[00m")
        return 0# ignore errors at this stage
    return 1

def print_stats(orig, res):#sizes
    print("\n\033[0;32mCompressed File from "+ str(round(orig / 1000000,2)) + "mb to "+ str(round(res / 1000000, 2)) + "mb (-"+str(round(100 - (res / orig * 100), 2))+"%)\033[00m")

def clean_up(folder):#removes the directory and files that were used in compression process
    print("--cleaning up--")
    shutil.rmtree(folder)

def log(err_string):
    with open("error.log","a") as f:
        f.write("\n"+str(datetime.now())[:-4]+err_string)

def get_paths(args):
    path = [rf"{os.path.abspath(args['path'])}"]
    output_path = rf"{args['output_path']}"
    is_dir = os.path.isdir(path[0])

    if is_dir:
        if output_path[-4:] == ".pdf":
            raise ValueError("OptionError: If path is a directory the outut must be one too!")
        if output_path == "default":
            output_path = os.path.abspath(path[0])+"_compressed"
        path = get_file_list(path[0],".pdf")
    elif not is_dir and output_path == "default":
        output_path = os.path.abspath(path[0][:-4])+"_compressed.pdf"
    elif not is_dir and not output_path[-4:] == ".pdf":#output is a directory
        output_path = os.path.join(os.path.abspath(output_path), path[0].split(s)[-1])
    
    return path, output_path, is_dir

def main(args):#TODO always use prefix absolute file path
    path, output_path, is_dir = get_paths(args)
    
    if len(path) == 0:
        print("No PDF Found!")
        print(path)
        print(output_path)
    force_ocr = args["force_ocr"]
    
    for pdf_file in path[args["continue"]:]:
        print("--Compressing \033[0;33;33m%s\033[00m--" % pdf_file)#print filename in yellow
        orig_size = os.stat(pdf_file).st_size
        pdf_name = pdf_file[:-4].split(os.path.sep)[-1]#remove .pdf, path (only Filename)

        #folder for temporary files(images...)
        tmp_folder = (pdf_name + FOLDER_ENDING).replace(" ","_")
        #create it if not already exists
        if not os.path.isdir(tmp_folder):
            os.mkdir(tmp_folder)
        #split pdf into images
        pdf2img(pdf_file, pdf_name, tmp_folder, args["mode"])

        #list of pdf pages in png format
        imgs = get_file_list(tmp_folder,".png")
       
        print("--Compressing via Crunch--")
        pool = multiprocessing.Pool()
        try:
            # multithreaded compression of single images
            # parameter is function and splitted imgs list with some length counts to display progress
            pool.starmap(compress, zip(imgs, [ len(imgs) for x in range(len(imgs)) ], [ x for x in range(len(imgs)) ]))
        except KeyboardInterrupt:
            #shutil.rmtree(folder)#clean up
            pool.terminate()
            quit()
        except Exception as e:
            #shutil.rmtree(folder)#clean up after failure
            raise e
        finally: # To make sure processes are closed in the end, even if errors happen
            pool.close()
            pool.join()
            print("** - 100%")

        output_file = output_path
        if is_dir:
            output_file = os.path.join(output_path, pdf_name)+".pdf"
        #create if not exists #TODO refactor to func
        if not os.path.isdir(os.path.dirname(output_file)):
            os.mkdir(os.path.dirname(output_file))
        
        # merge images/pages into new pdf and apply OCR
        img2pdf(pdf_name,imgs, output_file)
        # compress lossless
        cpdfsqueeze(output_file)
        # disgard progress if not smaller. try simple compression with cpdfsqueeze instead
        if os.stat(pdf_file).st_size < os.stat(output_file).st_size and not force_ocr:
            if not cpdfsqueeze(pdf_file, output_file):
                shutil.copy(pdf_file,output_file)
            print("\033[0;31mNo OCR created.\033[00m")
        clean_up(tmp_folder)
        print("created \033[0;33;33m%s\033[0;m " % output_path)
        print_stats(orig_size, os.stat(output_file).st_size)

if __name__ == "__main__":
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
    if USE_PY_TESS:
        if args["no_ocr"]:# switch off OCR
            USE_PY_TESS = False
        elif not init_pytesseract(args):
            all_args.print_help()
    main(args)