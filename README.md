# Pdf-Compressor
A Modular File processing tool. Enables file upload processing via plugins and download.

# Installation

### Overview
1. [clone Repo](#1-clone-repo)
2. [Install python packages](#2-install-python-packages)
3. [Webserver Setup](#3-webserver-setup)
4. [Setup Your Plugins](#4-Setup-Your-Plugins)

----
### 1. Clone Repo
```bash
git clone https://github.com/pIlIp-d/PDF-Compressor
```

----
### 2. Install Python Packages
```bash
cd <project-directory>
pip install -r requirements.txt
```
or for specific python version 3.10
```bash
python3.10 -m pip install -r requirements.txt
```

----

### 3. Webserver Setup
Setting up the Django DB
```bash
python3 manage.py makemigrations
python3 manage.py migrate
```

Start the webserver
```bash
python3 manage.py runserver
```

### 4. Setup Your Plugins

To use the processing you can use [existing plugins](#List-of-known-Plugins) or create your own.
The existing plugins may need to be configured. For that look inside the documentation of the plugin itself.

----
# More Documentation

How to create your own Plugin is documented [here](documentation/Plugin.md).  
More Documentation can be found [here](documentation/README.md).  


----

# List of known Plugins

| Plugin Name      | Description                                                                                                        | Path, Info and Documentation                                       | Credits                                   |
|------------------|--------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------|-------------------------------------------|
| CrunchCompressor | Compression Plugin for Pdfs and Images that also enables Conversion from Pdfs to and from different Image Formats. | [./plugins/crunch_compressor](plugins/crunch_compressor/README.md) | [Philip Dell](https://github.com/pIlIp-d) |

