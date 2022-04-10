
# Pdf Compressor
Solves the problem with small Upload size limit or just to big files from GoodNotes export.  

It Takes its Time, but it is really the Best. (Crunch)  
... so I put it together with pdf2image and backwards to compress pdfs with crunch.

## Compression Rate

Goodnote Files with mode `extreme` are compressed to about 2% and are still clear enough for every application.  
`medium-high` compressses to about 7%. 

And if your really need your 600pdi you can use mode `low`


# Dependency

## External Dependencies

`Pngquant`,`Zopfli`,`Poppler`

## Python Packages

`pdf2image`,`img2pdf` and my version of `crunch` [(here)](./lib/crunch.py)

## Windows Setup

  Download latest [poppler release](https://github.com/oschwartz10612/poppler-windows/releases/)  

  Download [Pngquant](https://pngquant.org) Binary for Windows

  Download [Zopfli](https://drpleaserespect.github.io/posts/zopfli-and-zopflipng-windows-binaries/)


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
