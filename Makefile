define PRODUCTION_SETTINGS
# These settings assume sqlite, but have postgres settings commented out.
# If you want to use postgres, the following two lines are unnecessary
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

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

SECRET_KEY = 'k+&1)2^g5^a*4nl+vlz)_ezv8!bup(ttn0(byvm)(gx%&c)w-5'

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']
endef

export PRODUCTION_SETTINGS

skolagatt/production_settings.py:
	@echo "$$PRODUCTION_SETTINGS" > skolagatt/production_settings.py

check:
	pep8

venv: venv/bin/activate

venv/bin/activate: requirements.txt
	test -d venv || virtualenv venv
	venv/bin/pip install -Ur requirements.txt
	touch venv/bin/activate

test: venv skolagatt/production_settings.py
	./manage.py test common
