# CrunchCompressor
For Pdfs and PNGs.

Solves the problem with small Upload size limit or just too big files from GoodNotes export.
Pdf Compressor converts Pdfs to PNGs and uses lossy png compression. Afterwards it converts the PNGs back to pdfs and runs another round of lossless pdf compression.
Additionally, the program can apply OCR - Optical Character Recognition (creates searchable pdfs)

# Dependency

## External Dependencies

`Pngquant`, `AdvPNG`, `Pngcrush` are included for windows (and or linux when using wine)  
`cpdfsqueeze` needs `wine` on Linux  
`Tesseract` is optional for OCR - Optical Character Recognition and must be installed manually  

# Installation
1. [Installing Tesseract if you want OCR](#1-installing-tesseract)
2. [Install compression tools](#2-installing-compression-tools)
3. [run `config.py`](#3-configure-dependency-paths)
4. [Import Plugin into settings.py](#4-import-plugin-into-settings.py)

## 1. Installing Tesseract

### Windows via GUI
Download and Install [Tesseract](https://github.com/UB-Mannheim/tesseract/wiki)  
Select Additional Languages that you want. (f.e German under Additional Language Data)  

### Linux (Ubuntu)
```bash
apt install tesseract-ocr
```
add additional [language packs](https://tesseract-ocr.github.io/tessdoc/Data-Files-in-different-versions.html)
```bash
apt install tesseract-ocr-<language-shortform> -y

# example for german
apt install tesseract-ocr-deu -y
```

---
## 2. Installing Compression Tools
### windows
pre-installed in compressor_lib directory (paths are already configured)

### Linux(ubuntu)
```bash
apt install pngquant -y && apt install advancecomp -y && apt install pngcrush -y
# or
sudo apt install pngquant -y && sudo apt install advancecomp -y && sudo apt install pngcrush -y
```
install wine for cpdfsqueeze
```bash
apt install wine -y
```

---
## 3. Configure Dependency Paths
Try to run `python3 <plugin-path>/config.py` and if there are no error messages you're good to go.  

If there are errors or if you want to change a path you can configure it inside `config.py` by changing the paths for each dependency for your OS.  
You can also change `FORCE_WINE = True` to use the preinstalled executables.

## 4. Import Plugin into settings.py
this plugin enables 4 different plugins to be used.  
include the following lines into settings.py `PROCESSOR_PLUGINS` if you want to use all of them

```python
from plugin_system.plugins.crunch_compressor.plugin_config.plugin_config
    import PdfCompressorPlugin, PngCompressorPlugin, ImageToPdfConvertPlugin, PdfToImageConvertPlugin

PROCESSOR_PLUGINS = [
    # ... other plugins #
    PdfCompressorPlugin("pdf_compressor"),
    PngCompressorPlugin("png_compressor"),
    ImageToPdfConvertPlugin("png_to_pdf_converter"),
    PdfToImageConvertPlugin("pdf_to_image_converter")
]
```

-------------------------------------------------------------------------
# Usage via Command Line
run `<plugin_path>/__main__.py` to use PdfCompressor via the command line

## required parameters

    -p FileOrFolder

## Compression mode

----
Varies on Input of File and gets better with larger Files.  

change `-m` parameter to get higher compression or higher quality. Combine with `--force-ocr` or `--no-ocr` to ensure the result to be with ocr/without  

| parameter \ mode     | 1   | 2   | 3   | 4   | 5   |
|:---------------------|-----|-----|-----|-----|-----|
|                      |     |     |     |     |     |
| pngquant speed       | 1   | 2   | 2   | 8   | 9   |
| pngquant min-quality | 0   | 25  | 25  | 25  | 25  |
| pngquant max-quality | 80  | 85  | 85  | 90  | 99  |
|                      |     |     |     |     |     |
| advcomp shrink-rate  | 4   | 3   | 2   | 2   | 1   |
| advcomp iterations   | 3   | 2   | 1   | 1   | 1   |

if no special ocr mode is activated the pdf gets compressed through png split... and if the result is larger than the original the result gets replaced with a pdf that only is compressed via lossless pdf cpdfsqeeze.  
smaller or larger according to your pdf file.  
But be aware tiny files get Larger when the `--dpi` is set too high(~low compression).  
Small DPI means lower overall resolution.  
-> no OCR is saved and old document just gets compressed via cpdfsqeeze.  
Solution `-f` / `--force-ocd`


## Help
```
-h --help                  show this help message and exit
-p --path                  Path to pdf file or to folder containing pdf files
-m --mode                  compression mode 1-5. 1:high compression but slow 5:lower compression but fast. Default=5
-o --output-path           Compressed file Output Path. Default: 'filename_smaller.pdf' or
                           'compressed/...' for folders
-f --force-ocr             When turned on allows output file to be larger than input file, to force
                           ocr. Default: off and only smaller output files are saved.'
-n --no-ocr                Don't create OCR on pdf.
-q --quiet-mode            Don't print to console. Doesn't apply to Exceptions.
-l --tesseract-language    Language to create OCR with. Find the string for your language 
                           https://tesseract-ocr.github.io/tessdoc/Data-Files-in-different-versions.html.
                           Make sure it it installed.
-s --simple-and-lossless   Simple and lossless compression is non-invasive and skips the image converting.
                           Not as effective but simple and faster.
-d DPI --dpi DPI           DPI to use in conversion from pdf to images. Default=400.
```

## Examples
```
#default mode default output
python3 pdf_converter.py -p mypdf.pdf
#custom Mode and Output
python3 pdf_converter.py -p 'mypdf.pdf' -m 5 -o compressed_and_crisp.pdf

# for scanned pdfs or handwriting the --dpi parameter can be used for extreme compression
```

# Software License Agreements
**PDF-Compressor** https://github.com/pIlIp-d/PDF-Compressor <br>
Copyright (C) 2022 MIT - Philip Dell (https://github.com/pIlIp-d)

**pngquant** – https://pngquant.org <br>
Special Licence see [https://github.com/pIlIp-d/compressor-lib/blob/bf42fbf4e72fa215cad6fa64396ab091188687f4/pngquant/LICENCE.txt]("https://github.com/pIlIp-d/compressor-lib/blob/bf42fbf4e72fa215cad6fa64396ab091188687f4/pngquant/LICENCE.txt")

**advpng** – http://www.advancemame.it/download <br>
Copyright (C) 2007 Free Software Foundation, Inc. <http://fsf.org/> GPL v3

**pngcrush** – https://pmt.sourceforge.io/pngcrush <br>
Special Licence see [https://github.com/pIlIp-d/PDF-Compressor/blob/868aa5c42b28135150e5780e3cc7e967d2fb6586/pdfcompressor/compressor/compressor_lib/pngcrush/LICENCE.txt]("https://github.com/pIlIp-d/PDF-Compressor/blob/868aa5c42b28135150e5780e3cc7e967d2fb6586/pdfcompressor/compressor/compressor_lib/pngcrush/LICENCE.txt")

**cpdfsqeeze** – https://github.com/coherentgraphics/cpdfsqueeze-binaries <br>
Copyright (C) 2007 Free Software Foundation, Inc. <http://fsf.org/> LGPL

**crunch** – https://github.com/chrissimpkins/Crunch <br>
Copyright 2019 Christopher Simpkins - MIT License  
Only the **original Design** is used.

# Downloads
* [Pngquant](https://pngquant.org)
* [advpng](http://www.advancemame.it/download)
* [pngcrush](https://sourceforge.net/projects/pmt/files/pngcrush-executables/1.8.11/)
* [cpdfsqueeze](https://github.com/coherentgraphics/cpdfsqueeze-binaries)
* [crunch](https://github.com/pIlIp-d/compressor-lib/blob/f08adc46f6e865b5740671e7c15145b32541c237/crunch.py)


