# -*- coding: utf-8 -*-
import os
from . import production_settings

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = production_settings.SECRET_KEY

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = production_settings.DEBUG

ALLOWED_HOSTS = production_settings.ALLOWED_HOSTS


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'froala_editor',
    'common',
    'schools',
    'supportandexception',
    'samraemd',
    'survey',
]

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'skolagatt.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'schools.context_processors.user_school_permissions',
            ],
        },
    },
]

WSGI_APPLICATION = 'skolagatt.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases
DATABASES = production_settings.DATABASES


AUTHENTICATION_BACKENDS = [
    'skolagatt.backends.IceKeyAuth',
]

# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

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

CACHES = {
    'default': {
        'BACKEND': 'redis_cache.RedisCache',
        'LOCATION': 'redis:///',
    },
}

# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'is_IS'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

SESSION_COOKIE_AGE = 90 * 60  # Session will expiry after 90 minutes idle.

# SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

SUBDIRECTORY = ''

STATIC_ROOT = os.path.join(os.path.dirname(BASE_DIR), 'skolagatt/public/static')
STATIC_URL = '/static/'
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'skolagatt/static'),
    os.path.join(BASE_DIR, 'schools/static'),
    os.path.join(BASE_DIR, 'supportandexception/static'),
    os.path.join(BASE_DIR, 'samraemd/static'),
    os.path.join(BASE_DIR, 'survey/static'),
    os.path.join(BASE_DIR, 'vendor'),
    os.path.join(BASE_DIR, 'static'),
)
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.CachedStaticFilesStorage'

JSON_API_KEY = 'some-random-string'

ICEKEY_VERIFICATION = 'https://innskraning.mms.is/verify_login/'
ICEKEY_LOGIN = 'https://innskraning.mms.is/island_innskraning'

FROALA_UPLOAD_PATH = 'uploads/froala_editor/images/'
FROALA_INCLUDE_JQUERY = False

# Celery settings

CELERY_BROKER_URL = 'redis:///'
CELERY_RESULT_BACKEND = 'redis:///'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
