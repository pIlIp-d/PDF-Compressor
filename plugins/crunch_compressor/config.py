import os
from types import SimpleNamespace

import jsons

CONFIG_FILE = os.path.join(os.path.dirname(__file__), ".", "config.json")
FORCE_WINE = False


def get_config(config_file: str = CONFIG_FILE):
    config_path = os.path.abspath(config_file)
    if not os.path.isfile(config_path):
        raise FileNotFoundError("Config file not found. Run config.py in the crunch_compressor folder to configure "
                                "the necessary paths.")

    class Config:
        def __init__(self, advpng_path, pngquant_path, pngcrush_path, cpdfsqueeze_path, tesseract_path, tessdata_prefix,
                     wine_path):
            self.advpng_path = advpng_path
            self.pngquant_path = pngquant_path
            self.pngcrush_path = pngcrush_path
            self.cpdfsqueeze_path = cpdfsqueeze_path
            self.tesseract_path = tesseract_path
            self.tessdata_prefix = tessdata_prefix
            self.wine_path = wine_path

    with open(config_path, "r") as config_file:
        obj = jsons.loads(config_file.read(), object_hook=lambda d: SimpleNamespace(**d))
    return Config(**obj)


def check_existence(path, error_message) -> str:
    if not os.path.exists(path):
        if os.name != "nt":
            error_message += " If you're running the configuration with sudo, try it without."
        print(error_message)
        return ""  # Not Found
    else:
        return path


def main():
    compressor_lib_path = os.path.abspath(os.path.join(
        os.path.dirname(__file__), "compressor", "compressor_lib"
    ))

    cpdfsqueeze_path = check_existence(
        path=os.path.join(compressor_lib_path, "cpdfsqueeze", "cpdfsqueeze.exe"),
        error_message="cpdfsqueeze path not found. You need to install or download it. cpdfsqueeze.exe run by wine"
    )
    wine_path = ""
    if os.name == "nt" or FORCE_WINE:
        # WINDOWS
        pngquant_path = check_existence(
            os.path.join(compressor_lib_path, "pngquant", "pngquant.exe"),
            "Pngquant wasn't found. check README.md for help."
        )
        advpng_path = check_existence(
            os.path.join(compressor_lib_path, "advpng", "advpng.exe"),
            "Advpng wasn't found. check README.md for help."
        )
        pngcrush_path = check_existence(
            os.path.join(compressor_lib_path, "pngcrush", "pngcrush.exe"),
            "Pngcrush wasn't found. check README.md for help."
        )
        tesseract_path = check_existence(
            os.path.join(os.path.abspath(os.path.expanduser('~')), "AppData", "Local", "Programs", "Tesseract-OCR",
                         "tesseract.exe"),
            "Tesseract wasn't found. check README.md for help."
        )
        tessdata_prefix = "--tessdata-dir '" + check_existence(
            os.path.join(os.path.expanduser('~'), 'AppData', 'Local', 'Programs', 'Tesseract-OCR', 'tessdata'),
            "Tessdata Folder wasn't found. check README.md for help."
        ) + "'"
        if FORCE_WINE:
            wine_path = check_existence(
                path=os.path.join("/", "usr", "bin", "wine"),
                error_message="wine wasn't found and is needed for FORCE_WINE. Install it with 'sudo apt install wine'."
            )
            pngquant_path = wine_path + pngquant_path
            advpng_path = wine_path + advpng_path
            pngcrush_path = wine_path + pngcrush_path
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
        pngcrush_path = check_existence(
            path=os.path.join("/", "usr", "bin", "pngcrush"),
            error_message="pngcrush path not found. Install it with 'sudo apt install pngcrush'."
        )
        tesseract_path = check_existence(
            path=os.path.join("/", "usr", "bin", "tesseract"),
            error_message="pytesseract path not found. Install it with 'sudo apt install "
                          "tesseract-ocr'. Additionally add language packs with f.e. "
                          "'german/deutsch': 'sudo apt install tesseract-ocr-deu'"
        )
        wine_path = check_existence(
            path=os.path.join("/", "usr", "bin", "wine"),
            error_message="wine wasn't found and is needed for cpdfsqueeze. Install it with 'sudo apt install wine'."
        )
        tessdata_prefix = ""

    with open(os.path.join(os.path.dirname(__file__), "config.json"), "w") as config_file:
        config_string = "{" + rf'''
        "advpng_path" : "{advpng_path}",
        "pngquant_path" : "{pngquant_path}",
        "pngcrush_path" : "{pngcrush_path}",
        "cpdfsqueeze_path" : "{cpdfsqueeze_path}",
        "tesseract_path" : "{tesseract_path}",
        "tessdata_prefix" : "{tessdata_prefix}",
        "wine_path" : "{wine_path}"
    ''' + "}"
        config_file.write(config_string.replace("\\", "\\\\"))
    print(f"PluginConfig finished and saved to %s/config.json" % os.path.dirname(__file__))


if __name__ == "__main__":
    main()
