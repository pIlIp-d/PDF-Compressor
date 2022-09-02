# Web App Requirements

## Features

* public mode
  * visible in local network as specified
  * files are uploaded compressed and stored until there downloaded
  * store device via cookie to allow file download after timedelay and clean stored files after specified time
  
* local mode
  * relative paths can be used (no file upload and download)

## UI

* webui via Django
* all parameters as checkbox or textarea
* file upload and download grid/menu
* display exception when they occur

## Parameters

**PDFCompressor**
* all parameters of the class PDFCompressor
* boolean as checkbox
* fixed string values or int  ranges as select (maybe dynamically by looking up values(f.e tesseract languages))
* other values as textarea

* destination path
  * not a parameter given in web ui
  * textfield for optional file ending (empty is possible)
  * inside Django it is ./App/temporary_files/...

**optionally PDF-PNG Converter and crunch PNG compressor**  
* same parameters but for different classes
