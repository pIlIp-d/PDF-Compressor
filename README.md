
# Pdf Compressor
Solves the problem with small Upload size limit or just to big files from GoodNotes export.  

It Takes its Time, but it is really the Best. (Crunch)  
... so I put it together with pdf2image and backwards to compress pdfs with crunch.

## Compression Rate for Tested Goodnotes Files  

| Mode   | Rate |  from | to|
|:-------:|:----:|:----:|:--:|
|`extreme`| 95%. |2.84mb|0.34mb|
|`normal` | 70-95%.|2.84mb|0.67mb|
|`medium` | 40-60%.|2.84mb|1.13mb|
|`low`    | 10%.| 2.84mb|2.57mb|

varies on Input of File and gets better with larger Files.

And if your really need your 600dpi you can use mode `low`


# Dependency

## External Dependencies

`Pngquant`,`Zopfli`,`Poppler`,`Tesseract`

## Python Packages

`pdf2image`, `img2pdf`, `pytesseract`, `PyPDF4` and my version of `crunch` [(here)](./lib/crunch.py)

## Windows Setup

  Download latest [poppler release](https://github.com/oschwartz10612/poppler-windows/releases/)  

  Download [Pngquant](https://pngquant.org) Binary for Windows

  Download [Zopfli](https://drpleaserespect.github.io/posts/zopfli-and-zopflipng-windows-binaries/)

  Install [Tesseract](https://github.com/UB-Mannheim/tesseract/wiki)  
  Select Additional Languages that you want. (f.e German under Additional Language Data)  

### Folder Structure

Extract and place all the file as show below.

```
├── lib
│   ├── pngquant
│   │   └── ...
│   ├── poppler-xx.xx.x
│   │   └── ...
│   ├── crunch.py
│   └── zopfli.exe
└── pdf_converter.py
```


# Usage

```
 -h, --help            show this help message and exit
  -f FILE, --file FILE  path to pdf file
  -m MODE, --mode MODE  compression mode ['low', 'medium', 'standard', 'high', 'extreme']
  -o OUTPUT_FILE, --output-file OUTPUT_FILE
                        Compressed file Output Path. Default: 'filename_smaller.pdf'
```
 

Example 
```
python3 pdf_converter.py -f mypdf.pdf
```


# problem Fixing

If Tesseract isnt working you need to edit pdf_converter.py `TESSERACT_PATH` to your path
linux might work entirely different
