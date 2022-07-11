from setuptools import setup
from setuptools import find_packages

setup(
  name="pdfcompressor",
  description="Compresses PDFs extremely.",
  url="https://github.com/pIlIp-d/PDF-Compressor",
  author="pIlIp-d",
  license="MIT",
  python_requires='>=3.10',
  platforms=["any"],
  packages=find_packages(),
  install_requires=["pillow", "PyMuPdf", "img2pdf", "pandas", "pytesseract"],
  include_package_data=True,
  classifiers=[
    "License :: MIT",
    "Topic :: Software Development :: Libraries :: Python Module",
    "Topic :: Utilities :: Compression",
    "Programming Language :: Python :: 3"
  ]
)
