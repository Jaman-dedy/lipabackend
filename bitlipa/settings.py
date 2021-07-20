"""
Django settings for bitlipa project.

Generated by 'django-admin startproject' using Django 3.2.4.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

import os
from pathlib import Path
import environ
import dj_database_url
import moneyed


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Initialise environment variables
env = environ.Env()

if os.path.exists(f'{BASE_DIR}/.env'):
    environ.Env.read_env(f'{BASE_DIR}/.env')


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY', default='bitlipa-secret')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool('DEBUG', default=False)

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default='*')
API_URL = env('API_URL', default='http://localhost:8000/api/v1')
APP_NAME = env('APP_NAME', default='BitLipa')
MOBILE_APP_URL = env('MOBILE_APP_URL', default='intent://bitlipa.africa/#Intent;scheme=bitlipa;package=africa.bitlipa;end')
MOBILE_APP_HASH = env('MOBILE_APP_HASH', default='')
THRESH0LD_API = env('THRESH0LD_API', default='')

# Application definition
INSTALLED_APPS = [
    'rest_framework',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'djmoney',
    'bitlipa.apps.otp',
    'bitlipa.apps.authentication',
    'bitlipa.apps.users',
    'bitlipa.apps.fiat_wallet',
    'bitlipa.apps.crypto_wallets',
    'bitlipa.apps.transactions'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # custom middlewares
    'bitlipa.middlewares.http_error_handler.HTTPErrorHandler',
]

REST_FRAMEWORK = {
    'EXCEPTION_HANDLER': lambda e, _: exec('raise e')
}

ROOT_URLCONF = 'bitlipa.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(Path(__file__).resolve().parent, 'templates')],
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

WSGI_APPLICATION = 'bitlipa.wsgi.application'

if DEBUG:
    LOGGING = {
        'version': 1,
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
            },
        },
        'loggers': {
            'django.db.backends': {
                'level': 'DEBUG',
            },
        },
        'root': {
            'handlers': ['console'],
        }
    }

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': env('DB_ENGINE', default='django.db.backends.postgresql_psycopg2'),
        'NAME': env('DB_NAME', default='bitlipa'),
        'USER': env('DB_USER', default='postgres'),
        'PASSWORD': env('DB_PASSWORD', default=''),
        'HOST': env('DB_HOST', default='localhost', ),
        'PORT': env('DB_PORT', default='5432'),
    }
}

prod_db = dj_database_url.config(conn_max_age=500)
DATABASES['default'].update(prod_db)


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


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/


STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

EMAIL_USE_TLS = True
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = env('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default=SECRET_KEY)
EMAIL_HOST_USER = env('EMAIL_HOST_USER', default='contact@bitlipa.com')
EMAIL_PORT = env.int('EMAIL_PORT', default=587)

EMAIL_SENDER = env('EMAIL_SENDER', default='noreply@bitlipa.com')

TWILIO_ACCOUNT_SID = env("TWILIO_ACCOUNT_SID", default="")
TWILIO_AUTH_TOKEN = env("TWILIO_AUTH_TOKEN", default="")
TWILIO_NUMBER = env("TWILIO_NUMBER", default="")
SMS_BROADCAST_TO_NUMBERS = []

moneyed.add_currency(code='ETH', numeric='0001', name='Ethereum', countries=())
moneyed.add_currency(code='BTC', numeric='0002', name='Bitcoin', countries=())
moneyed.add_currency(code='TET', numeric='0003', name='Tether', countries=())
