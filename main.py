import re

stdout = """
--------------------------------------------------------------------
BLP
Extensions: .blp
Features: open, save, encode
--------------------------------------------------------------------
BMP image/bmp
Extensions: .bmp
Features: open, save
--------------------------------------------------------------------
BUFR
Extensions: .bufr
Features: open, save
--------------------------------------------------------------------
CUR
Extensions: .cur
Features: open
--------------------------------------------------------------------
DCX
Extensions: .dcx
Features: open
--------------------------------------------------------------------
DDS
Extensions: .dds
Features: open, save
--------------------------------------------------------------------
DIB image/bmp
Extensions: .dib
Features: open, save
--------------------------------------------------------------------
EPS application/postscript
Extensions: .eps, .ps
Features: open, save
--------------------------------------------------------------------
FITS
Extensions: .fit, .fits
Features: open, save
--------------------------------------------------------------------
FLI
Extensions: .flc, .fli
Features: open
--------------------------------------------------------------------
FPX
Extensions: .fpx
Features: open
--------------------------------------------------------------------
FTEX
Extensions: .ftc, .ftu
Features: open
--------------------------------------------------------------------
GBR
Extensions: .gbr
Features: open
--------------------------------------------------------------------
GIF image/gif
Extensions: .gif
Features: open, save, save_all
--------------------------------------------------------------------
GRIB
Extensions: .grib
Features: open, save
--------------------------------------------------------------------
HDF5
Extensions: .h5, .hdf
Features: open, save
--------------------------------------------------------------------
ICNS image/icns
Extensions: .icns
Features: open, save
--------------------------------------------------------------------
ICO image/x-icon
Extensions: .ico
Features: open, save
--------------------------------------------------------------------
IM
Extensions: .im
Features: open, save
--------------------------------------------------------------------
IMT
Features: open
--------------------------------------------------------------------
IPTC
Extensions: .iim
Features: open
--------------------------------------------------------------------
JPEG image/jpeg
Extensions: .jfif, .jpe, .jpeg, .jpg
Features: open, save
--------------------------------------------------------------------
JPEG2000 image/jp2
Extensions: .j2c, .j2k, .jp2, .jpc, .jpf, .jpx
Features: open, save
--------------------------------------------------------------------
MCIDAS
Features: open
--------------------------------------------------------------------
MIC
Extensions: .mic
Features: open
--------------------------------------------------------------------
MPEG video/mpeg
Extensions: .mpeg, .mpg
Features: open
--------------------------------------------------------------------
MSP
Extensions: .msp
Features: open, save, decode
--------------------------------------------------------------------
PCD
Extensions: .pcd
Features: open
--------------------------------------------------------------------
PCX image/x-pcx
Extensions: .pcx
Features: open, save
--------------------------------------------------------------------
PIXAR
Extensions: .pxr
Features: open
--------------------------------------------------------------------
PNG image/png
Extensions: .apng, .png
Features: open, save, save_all
--------------------------------------------------------------------
PPM image/x-portable-anymap
Extensions: .pbm, .pgm, .pnm, .ppm
Features: open, save
--------------------------------------------------------------------
PSD image/vnd.adobe.photoshop
Extensions: .psd
Features: open
--------------------------------------------------------------------
SGI image/sgi
Extensions: .bw, .rgb, .rgba, .sgi
Features: open, save
--------------------------------------------------------------------
SPIDER
Features: open, save
--------------------------------------------------------------------
SUN
Extensions: .ras
Features: open
--------------------------------------------------------------------
TGA image/x-tga
Extensions: .icb, .tga, .vda, .vst
Features: open, save
--------------------------------------------------------------------
TIFF image/tiff
Extensions: .tif, .tiff
Features: open, save, save_all
--------------------------------------------------------------------
WEBP image/webp
Extensions: .webp
Features: open, save, save_all
--------------------------------------------------------------------
WMF
Extensions: .emf, .wmf
Features: open, save
--------------------------------------------------------------------
XBM image/xbm
Extensions: .xbm
Features: open, save
--------------------------------------------------------------------
XPM image/xpm
Extensions: .xpm
Features: open
--------------------------------------------------------------------
XVTHUMB
Features: open
--------------------------------------------------------------------
"""


if __name__ == '__main__':
    feature_list = re.split("-+", stdout)
    supported_extensions = []
    supported_mime_types = []
    for feature_item in feature_list:
        feature_description = feature_item.split("Features:")[-1]
        if "open" in feature_description and "save" in feature_description:
            if "Extensions:" in feature_item:
                types = feature_item.split("Extensions:")[0].split(" ")
                extensions = feature_item.split("Extensions:")[1].split("\n")[0]
                if len(types) > 1 and types[-1].startswith("image"):
                    for extension in extensions.split(" "):
                        if extension != '':
                            supported_extensions.append(extension.replace(",", ""))
                    supported_mime_types.append(types[-1].replace("\n", ""))

    print(list(set(supported_extensions)))
    print(list(set(supported_mime_types)))
