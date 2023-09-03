import argparse
import os.path
import shutil
import sys

from plugin_system.plugins.crunch_compressor.compressor.pdf_compressor.pdf_crunch_compressor import PDFCrunchCompressor

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
        help="compression mode 1-5. 1:high compression but slow 5:lower compression but fast. Default=5",
        default=5
    )
    all_args.add_argument(
        "-o", "--output-path",
        required=False,
        help="Compressed file Output Path. Default: 'filename_compressed.pdf' or 'compressed/...' for folders",
        default="default"
    )
    all_args.add_argument(
        "-f", "--force-ocr",
        required=False,
        default=False,
        action='store_true',
        help="When turned on allows output file to be larger than input file, to force ocr. "
             "Default: off and only smaller output files are saved.'"
    )
    all_args.add_argument(
        "-n", "--no-ocr",
        required=False,
        default=False,
        action='store_true',
        help="Don't create OCR on pdf."
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
    all_args.add_argument(
        "-s", "--simple-and-lossless",
        required=False,
        action='store_true',
        help="Simple and lossless compression is non-invasive and skips the image converting."
             "Not as effective but simple and faster."
    )
    all_args.add_argument(
        "-d", "--dpi",
        required=False,
        type=int,
        help="DPI to use in conversion from pdf to images. Default=350.",
        default=350
    )

    return vars(all_args.parse_args())


if __name__ == '__main__':
    try:
        args = get_args()
        if args["quiet_mode"]:
            sys.stdin.close()
            sys.stdout.close()

        PDFCrunchCompressor(
            compression_mode=args["mode"],
            force_ocr=args["force_ocr"],
            no_ocr=args["no_ocr"],
            tesseract_language=args["tesseract_language"],
            simple_and_lossless=args["simple_and_lossless"],
            default_pdf_dpi=args["dpi"]
        ).process(
            args["path"],
            args["output_path"]
        )

    except KeyboardInterrupt:
        while True:
            i = input("Do you want to cleanup the temporary Files created in the process? (Y/N)")
            if i.lower() == "y":
                # remove all directories ending with _tmp
                directories = [f.path for f in os.scandir("../../..") if f.is_dir() and "_tmp" in f.path]
                directories.append("./temporary_files")
                for d in directories:
                    if os.path.exists(d):
                        shutil.rmtree(d)
                        print(f"removed '{d}'")

                break
            elif i.lower() == "n":
                break
