import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '9g!57u34sefgiuay(d7bj4s5@#oaqybj8)sts63pjyi39l@ihd'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', 'skolagatt.is']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'common',
    'schools',
    'supportandexception',
    'samraemd',
    'survey'
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

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        # 'ENGINE'   : 'django.db.backends.postgresql_psycopg2',
        # 'NAME'     : 'skolagatt',
        # 'USER'     : 'user',  # Postgres user that has all privileges for the skolagatt DB
        # 'PASSWORD' : 'password',  # Password for Postgres user
        # 'HOST'     : 'localhost',  # Address of postgres server, defaults to localhost (for dev)
        # 'PORT'     : '5432',
    }
}


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


# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

SESSION_COOKIE_AGE = 60 * 30  # Session will expiry after 30 minutes idle.
SESSION_SAVE_EVERY_REQUEST = True

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
)


JSON_API_KEY = 'some-random-string'

ICEKEY_VERIFICATION = 'https://innskraning.mms.is/verify_login/'
ICEKEY_LOGIN = 'https://innskraning.mms.is/island_innskraning'
