from pdfcompressor.utility.ConsoleUtility import ConsoleUtility


class PytesseractNotFoundException(Exception):
    def __init__(self):
        super().__init__(ConsoleUtility.get_error_string(r"[ ! ] - tesseract Path not found. Install "
                                                         "https://github.com/UB-Mannheim/tesseract/wiki or edit "
                                                         "'TESSERACT_PATH' to your "
                                                         "specific tesseract executable"))
