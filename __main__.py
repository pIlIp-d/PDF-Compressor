import argparse
import os

from pdfcompressor.pdfcompressor import PDFCompressor
from pdfcompressor.utility.ConsoleUtility import ConsoleUtility

global PNGQUANT_PATH, ADVPNG_PATH, TESSERACT_PATH

if os.name == "nt":
    PNGQUANT_PATH = os.path.join(os.path.dirname(__file__), "compressor/compressor_lib", "pngquant", "pngquant.exe")
    ADVPNG_PATH = os.path.join(os.path.dirname(__file__), "compressor/compressor_lib", "advpng", "advpng.exe")
    TESSERACT_PATH = os.path.join(os.path.expanduser('~'), "AppData", "Local", "Programs", "Tesseract-OCR",
                                  "tesseract.exe")

else:
    PNGQUANT_PATH = os.path.join("/", "usr", "bin", "pngquant")
    ADVPNG_PATH = os.path.join("/", "usr", "bin", "advpng")
    TESSERACT_PATH = os.path.join(os.path.expanduser('~'), ".local", "bin", "pytesseract")
    # Linux: errors if paths weren't found
    if not os.path.exists(PNGQUANT_PATH):
        ConsoleUtility.print(
            ConsoleUtility.get_error_string("Pngquant path not found. Install it with 'sudo apt install pngquant'."))
        exit()
    if not os.path.exists(ADVPNG_PATH):
        ConsoleUtility.print(
            ConsoleUtility.get_error_string("advpng path not found. Install it with 'sudo apt install advancecomp'."))
        exit()
    if not os.path.exists(TESSERACT_PATH):
        ConsoleUtility.print(
            ConsoleUtility.get_error_string("pytesseract path not found. Install it with 'sudo apt install "
                                            "pytesseract-ocr'. Additionally add language packs with f.e. "
                                            "'german/deutsch': 'sudo apt install pytesseract-ocr-deu'"))
        exit()

CPDFSQUEEZE_PATH = os.path.join(os.path.dirname(__file__), "compressor/compressor_lib", "cpdfsqueeze",
                                "cpdfsqueeze.exe")


def get_args():
    all_args = argparse.ArgumentParser(
        prog='PDF Compress',
        usage='%(prog)s [options]',
        description='Compresses PDFs using lossy png and lossless PDF compression. Optimized for GoodNotes'
    )
    all_args.add_argument(
        "-p", "--path",
        required=True,
        help="Path to pdf file or to folder containing pdf files"
    )
    all_args.add_argument(
        "-m", "--mode",
        required=False,
        type=int,
        help="compression mode 1-10. 1:high 10:low compression. Default=3",
        default=3
    )
    all_args.add_argument(
        "-o", "--output-path",
        required=False,
        help="Compressed file Output Path. Default: 'filename_compressed.pdf' or 'compressed/...' for folders",
        default="default"
    )
    all_args.add_argument(
        "-s", "--force-ocr",
        required=False,
        action='store_true',
        help="When turned on allows output file to be larger than input file, to force ocr. "
             "Default: off and only smaller output files are saved.'"
    )
    all_args.add_argument(
        "-n", "--no-ocr",
        required=False,
        action='store_true',
        help="Don't create OCR on pdf."
    )
    all_args.add_argument(
        "-c", "--continue",
        required=False,
        type=int,
        help="Number. When compressing folder and Interrupted, skip files already converted."
             " (=amount of files already converted)",
        default=0
    )
    all_args.add_argument(
        "-q", "--quiet-mode",
        required=False,
        action='store_true',
        help="Don't print to console. Doesn't apply to Exceptions."
    )
    all_args.add_argument(
        "-l", "--tesseract-language",
        required=False,
        default="deu",
        help="Language to create OCR with. Find the string for your language "
             "https://tesseract-ocr.github.io/tessdoc/Data-Files-in-different-versions.html. Make "
             "sure it it installed."
    )
    return vars(all_args.parse_args())


if __name__ == '__main__':
    args = get_args()
    PDFCompressor(
        args["path"],
        args["output_path"],
        args["mode"],
        args["continue"],
        args["force_ocr"],
        args["no_ocr"],
        args["quiet_mode"],
        args["tesseract_language"]
    )
