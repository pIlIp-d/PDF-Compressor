RED = "\033[0;31m"
END = "\033[0m"


class PytesseractNotFoundException(Exception):
    def __init__(self):
        super().__init__(RED + "[ ! ] - tesseract Path not found. Install "
                               "https://github.com/UB-Mannheim/tesseract/wiki or edit 'TESSERACT_PATH' to your "
                               "specific tesseract executable" + END)
