from setuptools import find_packages
from setuptools import setup

setup(
    version="2.3.0",
    name="pdfcompressor",
    description="Compresses PDFs extremely.",
    url="https://github.com/pIlIp-d/PDF-Compressor",
    author="pIlIp-d",
    license="MIT",
    python_requires='>=3.10',
    platforms=["any"],
    packages=find_packages(),
    install_requires=[
        "pillow",
        "PyMuPdf",
        "img2pdf",
        "pytesseract",
        "jsons"
    ],
    include_package_data=True,
    classifiers=[
        "License :: MIT",
        "Topic :: Software Development :: Libraries :: Python Module",
        "Topic :: Utilities :: Compression",
        "Programming Language :: Python :: 3"
    ]
)
