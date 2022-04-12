from setuptools import setup
from setuptools import find_packages

setup(
  name = "PDF Compressor",
  description = "Compresses PDFs, made for GoodNotes",
  url = "https://github.com/pIlIp-d/PDF-Compressor",
  author = "pIlIp-d",
  license = "MIT",
  python_requires='>=3.6',
  platforms = ["any"],
  packages = find_packages(),
  install_requires = ["PyMuPdf","pytesseract","img2pdf"],
  include_package_data = True,
  classifiers = [
    "License :: MIT",
    "Topic :: Software Development :: Libraries :: Python Module",
    "Topic :: Utilities",
    "Programming Language :: Python :: 3"
  ]
)
