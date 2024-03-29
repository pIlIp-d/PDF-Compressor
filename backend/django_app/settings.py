"""
Django settings for django_app project.

Generated by 'django-admin startproject' using Django 3.2.12.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""
from pathlib import Path

from plugin_system.plugins.crunch_compressor.plugin_config.plugin_config import PdfCompressorPlugin, \
    PngCompressorPlugin, \
    ImageToPdfConvertPlugin, PdfToImageConvertPlugin, GoodNotesCompressorPlugin
from plugin_system.plugins.ffmpeg_converter.plugin import FfmpegConverterPlugin
from plugin_system.plugins.image_converter.plugin import ImageConverterPlugin

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-0e_mwlj(=tv2-bys5n)s%ak6lib*#+w@=z1ptq@t4l56w!a9mk'

# SECURITY WARNING: don't run with debug turned on in production!

DEBUG = True

ALLOWED_HOSTS = ["*"]
TIME_FORMAT = "%d.%m.%Y-%H.%M.%S"

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'corsheaders',
    "django_app.webserver",
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_app.webserver.middlewares.UserIdMiddleware',
    'django_app.webserver.middlewares.RequestIdMiddleware',
]

FRONTEND_URL = "http://localhost:5173"
# allow requests from the frontend
CORS_ALLOW_CREDENTIALS = True
CORS_ORIGIN_WHITELIST = [FRONTEND_URL]

CSRF_TRUSTED_ORIGINS = [FRONTEND_URL]

ROOT_URLCONF = 'django_app.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'django_app.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'django_app' / 'models.sqlite3',
        'OPTIONS': {
            'timeout': 2,  # in seconds
            # see also
            # https://docs.python.org/3.7/library/sqlite3.html#sqlite3.connect
        }
    }
}

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'django_app' / 'media'

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

PROCESSOR_PLUGINS = {
    PdfCompressorPlugin("pdf_compressor"),
    PngCompressorPlugin("png_compressor"),
    ImageToPdfConvertPlugin("png_to_pdf_converter"),
    PdfToImageConvertPlugin("pdf_to_image_converter"),
    GoodNotesCompressorPlugin("goodnotes_compressor"),
    ImageConverterPlugin("image_converter"),
    FfmpegConverterPlugin("ffmpeg_converter")
}
