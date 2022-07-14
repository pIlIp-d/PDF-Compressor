import os

from pdfcompressor.utility.console_utility import ConsoleUtility


def check_existence(path, error_message) -> str:
    if not os.path.exists(path):
        ConsoleUtility.print(
            ConsoleUtility.get_error_string(error_message)
            + " If you're running it with sudo try it without."
        )
        return path
    else:
        return ""  # Not Found


compressor_lib_path = os.path.abspath(os.path.join(
    os.path.dirname(__file__), "pdfcompressor", "compressor", "compressor_lib"
))

cpdfsqueeze_path = check_existence(
    path=os.path.join(compressor_lib_path, "cpdfsqueeze", "cpdfsqueeze.exe"),
    error_message="cpdfsqueeze path not found. You need to install or download it. cpdfsqueeze.exe run by wine"
)

if os.name == "nt":
    # WINDOWS
    pngquant_path = os.path.join(compressor_lib_path, "pngquant", "pngquant.exe")
    advpng_path = os.path.join(compressor_lib_path, "pdfcompressor", "compressor", "compressor_lib", "advpng", "advpng.exe")
    tesseract_path = os.path.join(os.path.abspath(os.path.expanduser('~')), "AppData", "Local", "Programs",
                                  "Tesseract-OCR", "tesseract.exe")
    tessdata_prefix = f"--tessdata-dir '{os.path.join(os.path.expanduser('~'), 'AppData', 'Local', 'Programs', 'Tesseract-OCR', 'tessdata')}'"

else:
    # LINUX
    pngquant_path = check_existence(
        path=os.path.join("/", "usr", "bin", "pngquant"),
        error_message="Pngquant path not found. Install it with 'sudo apt install pngquant'."
    )
    advpng_path = check_existence(
        path=os.path.join("/", "usr", "bin", "advpng"),
        error_message="advpng path not found. Install it with 'sudo apt install advancecomp'."
    )
    tesseract_path = check_existence(
        path=os.path.join(os.path.abspath(os.path.expanduser('~')), ".local", "bin", "pytesseract"),
        error_message="pytesseract path not found. Install it with 'sudo apt install "
                      "pytesseract-ocr'. Additionally add language packs with f.e. "
                      "'german/deutsch': 'sudo apt install pytesseract-ocr-deu'"
    )
    tessdata_prefix = ""

print("advpng, pngquant, cpdfsqueeze and tesseract were found and their paths were saved to config.json")
with open("config.json", "w") as config_file:
    config_file.write(
        "{" + f'''
    "advpng_path" : "{advpng_path}",
    "pngquant_path" : "{pngquant_path}",
    "cpdfsqueeze_path" : "{cpdfsqueeze_path}",
    "tesseract_path" : "{tesseract_path}",
    "tessdata_prefix" : "{tessdata_prefix}"
''' + "}"
    )
