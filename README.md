# Pdf-Compressor

A Modular File processing tool. Enables file upload processing via plugins and download.


It's important to note that some file conversions may result in loss of quality or data, especially when converting
between different file types that are not compatible with each other. Therefore, it's always a good idea to test the
output file after conversion to make sure it meets your requirements.

# Installation

### Overview

1. [clone Repo](#1-clone-repo)
2. [Install Docker and Docker Compose](#2-install-docker-and-docker-compose)
3. [Starting the Project](#3-starting-the-project)
4. [Setup Your Plugins](#4-Setup-Your-Plugins)

----

### 1. Clone Repo

```bash
git clone https://github.com/pIlIp-d/PDF-Compressor
```

----

### 2. Install Docker and Docker Compose

```bash
sudo apt install docker.io docker-compose 
```

----

### 3. Starting the Project

```bash
#first start may take a while to build the project
docker-compose up

# optionally rebuild manually
docker-compose build --no-cache
```

now you have the backend and the fronend running
visit [http://localhost:5173](http://localhost:5173) to start using it.

### 4. Setup Your Plugins

To use the processing you can use [existing plugins](#List-of-known-Plugins) or create your own.
The existing plugins may need to be configured. For that look inside the documentation of the plugin itself.

----

# More Documentation

How to create your own Plugin is documented [here](documentation/Plugin.md).  
More Documentation can be found [here](documentation/README.md).


----

# List of known Plugins

| Plugin Name      | Description                                                                                                        | Path, Info and Documentation                                                                           | Credits                                   |
|------------------|--------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------|-------------------------------------------|
| CrunchCompressor | Compression Plugin for Pdfs and Images that also enables Conversion from Pdfs to and from different Image Formats. | [./backend/plugin_system/plugins/crunch_compressor](./backend/plugin_system/plugins/crunch_compressor) | [Philip Dell](https://github.com/pIlIp-d) |
| ImageConverter   | Convert Images and lots of other files with ImageMagick.                                                           | [./backend/plugin_system/plugins/image_converter](./backend/plugin_system/plugins/image_converter)     | [Philip Dell](https://github.com/pIlIp-d) |

