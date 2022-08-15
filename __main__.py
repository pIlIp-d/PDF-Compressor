import argparse
from pdfcompressor.pdfcompressor import PDFCompressor


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
    """ temporarily or permanent deactivated
    all_args.add_argument(
        "-c", "--continue",
        required=False,
        type=int,
        help="Number. When compressing folder and Interrupted, skip files already converted."
             " (=amount of files already converted)",
        default=0
    )
    """
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

    return vars(all_args.parse_args())


if __name__ == '__main__':
    try:
        args = get_args()
        pdf_compressor = PDFCompressor(
            args["path"],
            args["output_path"],
            args["mode"],
            args["force_ocr"],
            args["no_ocr"],
            args["quiet_mode"],
            args["tesseract_language"],
            args["simple_and_lossless"]
        )
        pdf_compressor.compress()

    except KeyboardInterrupt:
        while True:
            i = input("Do you want to cleanup the temporary Files created in the process? (Y/N)")
            if i.lower() == "y":
                # TODO cleanup
                print("Not implemented yet")
                break
            elif i.lower() == "n":
                break
