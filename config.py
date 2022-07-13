import os

from pdfcompressor.utility.console_utility import ConsoleUtility


def check_existence(path, error_message):
    if not os.path.exists(path):
        ConsoleUtility.print(
            ConsoleUtility.get_error_string(error_message)
            + " If you're running it with sudo try it without."
        )
        exit()


cpdfsqueeze_path = os.path.abspath(os.path.join(
    os.path.dirname(__file__),
    "pdfcompressor", "compressor", "compressor_lib", "cpdfsqueeze", "cpdfsqueeze.exe")
)
check_existence(
    cpdfsqueeze_path,
    "cpdfsqueeze path not found. You need to install or download it. cpdfsqueeze.exe run by wine"
)

if os.name == "nt":
    pngquant_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "compressor", "compressor_lib", "pngquant", "pngquant.exe")
    advpng_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "compressor", "compressor_lib", "advpng", "advpng.exe")
    tesseract_path = os.path.join(os.path.abspath(os.path.expanduser('~')), "AppData", "Local", "Programs", "Tesseract-OCR",
                                  "tesseract.exe")

else:
    pngquant_path = os.path.join("/", "usr", "bin", "pngquant")
    advpng_path = os.path.join("/", "usr", "bin", "advpng")
    tesseract_path = os.path.join(os.path.abspath(os.path.expanduser('~')), ".local", "bin", "pytesseract")
    # Linux: errors if paths weren't found
    check_existence(
        pngquant_path,
        "Pngquant path not found. Install it with 'sudo apt install pngquant'."
    )
    check_existence(
        advpng_path,
        "advpng path not found. Install it with 'sudo apt install advancecomp'."
    )
    check_existence(
        tesseract_path,
        "pytesseract path not found. Install it with 'sudo apt install "
        "pytesseract-ocr'. Additionally add language packs with f.e. "
        "'german/deutsch': 'sudo apt install pytesseract-ocr-deu'"
    )

print("advpng, pngquant, cpdfsqueeze and tesseract were found and their paths were saved to config.json")
with open("config.json", "w") as config_file:
    config_file.write(
        "{" + f'''
    "advpng_path" : "{advpng_path}",
    "pngquant_path" : "{pngquant_path}",
    "cpdfsqueeze_path" : "{cpdfsqueeze_path}",
    "tesseract_path" : "{tesseract_path}"
''' + "}"
    )
