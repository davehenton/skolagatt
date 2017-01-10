# Skólagátt

## Samskiptatæki milli menntamálastofnunnar og grunnskóla landsins

Upplýsingar hjá skolagatt@mms.is og https://mms.is


## Postgres setup
Gagnleg skref í að setja upp postgres grunn fyrir skólagáttina
```
apt-get install postgresql postgresql-contrib
sudo -su postgres
psql
CREATE DATABASE skolagatt;
# Create the user, but please pick a better one than 'user' with 'password' as password, at least for production
CREATE USER user WITH PASSWORD 'password';
alter role mmsadmin set client_encoding to 'utf8';
alter role mmsadmin set default_transaction_isolation to 'read committed';
alter role mmsadmin set timezone to 'GMT';
grant all privileges on database skolagatt to mmsadmin;
```

## production_settings.py
Til að vera ekki alltaf að lenda í conflicti með settings.py splittum við sér stillingum út úr settings.py og setjum þær í skolagatt/production_settings.py. Þetta er líka gert svo ekkki sé verið að committa t.d. lykilorðum í gagnagrunn o.s.frv.
Hingað til eru 3 breytur í production_settings.py:
- DATABASES
  - Fyrir gagnagrunnsstillingar
- SECRET_KEY
  - Leyndarmál sem ætti ekki að vera opið á Github
- DEBUG
  - Af því að maður er alltaf að breyta því

### Dæmi um production_settings.py
```
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
```
