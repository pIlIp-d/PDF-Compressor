
# Pdf Compressor
Solves the problem with small Upload size limit or just to big files from GoodNotes export.  

Pdf Compressor converts Pdfs to PNGs and uses lossy png compression. Afterwards it converts the PNGs back to pdfs and runs another round of lossless pdf compression.  


Additionally the program can add OCR - Optical Character Recognition (creates searchable pdfs)  


# Dependency

## External Dependencies

`Pngquant`, `AdvPNG`, `Tesseract`

pngquant/advPNG could be diasabled manually inside crunch.py -> worse compression results  
Tesseract is optional for OCR - Optical Character Recognition

## Python Packages

`PyMuPdf`, `img2pdf`, `pytesseract`, and my version of [crunch](./lib/crunch.py)

----
# Setup

Windows
1. clone Repo recusively
2. Installing Tesseract if you want OCR  
3. run setup.py

Linux/Mac and manual Windows
1. clone Repo
2. install dependencies
3. configuring Vaiables to binaries
4. run setup.py

##  Windows
----
### 1. Inlcuding all binaries
```
git clone --recursive https://github.com/pIlIp-d/PDF-Compressor
```

----
### 2. Installing Tesseract

Download and Install [Tesseract](https://github.com/UB-Mannheim/tesseract/wiki)  
Select Additional Languages that you want. (f.e German under Additional Language Data)  

----
### 3. Install Python Packages
 run 
 ```
 python3 setup.py install
 ```

----
## Linux/Mac and manual Windows

### **1. without any binaries**
```
git clone https://github.com/pIlIp-d/PDF-Compressor
```

### **2. download and install dependencies**

Download [Pngquant](https://pngquant.org)  

Download [advpng](http://www.advancemame.it/download)  

Install [cpdfsqueeze](https://github.com/coherentgraphics/cpdfsqueeze-binaries)

Download [](Crunch)

#### Install Tesseract
```
sudo apt install tesseract-ocr -y
```
or find your own installation canidate

----
### **3. conifgure variables**

open and edit `pdf_compressor.py`

change path variables to something like this
```
CPDFSQUEEZE_PATH ~./lib/cpdfsqueeze/cpdfsqeeze
PNGQUANT_PATH ~ ./lib/pngquant/pngquant
ADVPNG_PATH advpng ~ /lib/advpng/advpng

TESSERACT_PATH ~ /usr/share/tesseract-ocr/4.00/tesseract
TESSDATA_PREFIX ~ /usr/share/tesseract-ocr/4.00/tessdata
```

### Expected Folder Structure

Extract and place all the file as show below.(.exe or whatever binaries you have)

```
├── lib
│   ├── pngquant
│   │   └── pngquant.exe
│   ├── advpng
│   │   └── advpng.exe
│   ├── cpdfsqueeze
│   │   └── cpdfsqueeze.exe
│   └── crunch.py
└── pdf_converter.py
```

# Usage

## required parameters

    -f FileOrFolder

## compression rate

Varies on Input of File and gets better with larger Files.  

Extremly small files get Larger when the mode is set to high(~low compression).  
-> no OCR is saved and old document just gets compressed via cpdfsqeeze. 
Solution -s / --force-ocd

## Help
```
-h --help           show this help message and exit
-f --file           path to pdf file or to folder containing pdf files
-m --mode           compression mode 1-10. 1:high 10:low compression. Default=3
-o --output-file    Compressed file Output Path. Default: 'filename_smaller.pdf' or
                    'compressed/...' for folders
-s --force-ocr      When turned on allows output file to be larger than input file, to
                    force ocr. Default: off and only smaller output files are saved.'
-n --no-ocr         Don't create OCR on pdf.
-c --continue       Number. When compressing folder and Interrupted, skip files already
                    converted. (=amount of files already converted)
```


## Examples
```
python3 pdf_converter.py -f mypdf.pdf
python3 pdf_converter.py -f 'mypdf.pdf' -m 5 -o compressed_and_crisp.pdf
```

# Known Problems

* console output at compression stage isn't chronological (because of multiprocessing)

* sometimes KeyboardInterrupt only works if currently not in Crunch compression process

* pngquant sometimes fails to compress, program just skips it

# LICENCE
