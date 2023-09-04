FROM python:3.11

COPY backend/requirements.txt backend/manage.py /backend/
COPY backend/django_app /backend/django_app
COPY backend/plugin_system /backend/plugin_system


RUN apt-get update && apt-get install -y \
    pngquant advancecomp pngcrush wine \
    tesseract-ocr tesseract-ocr-deu tesseract-ocr-eng \
    imagemagick

WORKDIR /backend

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBTECODE 1
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt
RUN python3 manage.py makemigrations
RUN python3 manage.py migrate

RUN python3 plugin_system/plugins/crunch_compressor/config.py
