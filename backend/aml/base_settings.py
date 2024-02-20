"""
Django settings for aml project.

Generated by 'django-admin startproject' using Django 3.0.3.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os
import logging
from corsheaders.defaults import default_headers
import sentry_sdk

logger = logging.getLogger(__name__)

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("AML_SECRET_KEY", 'topsecret')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('AML_DEBUG', '') != 'False'

ALLOWED_HOSTS = os.getenv("AML_ALLOWED_HOSTS", "localhost").split(",")

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.humanize',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'inline_actions',
    'corsheaders',
    'experiment',
    'participant',
    'result',
    'session',
    'section'
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'aml.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'aml.wsgi.application'


# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.0/topics/i18n/

# LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Europe/Amsterdam'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Increase django limits for large data sets
# A request timeout should be set in the webserver

DATA_UPLOAD_MAX_NUMBER_FIELDS = 32768
DATA_UPLOAD_MAX_MEMORY_SIZE = 512000000
FILE_UPLOAD_MAX_MEMORY_SIZE = 512000000


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = '/static/'

# Added to run : python manage.py collectstatic
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
MEDIA_ROOT = os.path.join(BASE_DIR, 'upload')
MEDIA_URL = '/upload/'

# Geoip service
LOCATION_PROVIDER = os.getenv("AML_LOCATION_PROVIDER", "")

# From mail address, used for sending mails
FROM_MAIL = 'name@example.com'
CONTACT_MAIL = FROM_MAIL

# Target url participants will be redirected to after reloading their user-session
RELOAD_PARTICIPANT_TARGET = 'https://app.amsterdammusiclab.nl'
HOMEPAGE = 'https://www.amsterdammusiclab.nl'

# CORS origin white list from .env
CORS_ORIGIN_WHITELIST = os.getenv(
    "AML_CORS_ORIGIN_WHITELIST",
    "http://localhost:3000,http://127.0.0.1:3000,{}".format(HOMEPAGE)
).split(",")

# CORS
CORS_ORIGIN_ALLOW_ALL = False
CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_HEADERS = list(default_headers) + [
    'sentry-trace',
    'baggage',
]

SESSION_SAVE_EVERY_REQUEST = False # Do not set to True, because it will break session-based participant_id

CSRF_USE_SESSIONS = False

LOCALE_PATHS = [os.path.join(BASE_DIR, 'locale')]

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

if os.getenv("SENTRY_DSN"):
    sentry_sdk.init(
        dsn=os.getenv("SENTRY_DSN", ""),
        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        traces_sample_rate=0.2,
        # Set profiles_sample_rate to 1.0 to profile 100%
        # of sampled transactions.
        # We recommend adjusting this value in production.
        profiles_sample_rate=0.2,
    )
else:
    logger.info("SENTRY_DSN is not defined. Skipping Sentry initialization.")

SUBPATH = os.getenv('AML_SUBPATH', None)
