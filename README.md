[![Build Status](https://travis-ci.org/menntamalastofnun/skolagatt.svg?branch=master)](https://travis-ci.org/menntamalastofnun/skolagatt) [![Code Climate](https://codeclimate.com/github/menntamalastofnun/skolagatt/badges/gpa.svg)](https://codeclimate.com/github/menntamalastofnun/skolagatt)

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

## Aðrir pakkar
Aðrir pakkar sem þarf að setja upp eru Celery og Redis.

## production_settings.py
Til að vera ekki alltaf að lenda í conflicti með settings.py splittum við sér stillingum út úr settings.py og setjum þær í skolagatt/production_settings.py. Þetta er líka gert svo ekki sé verið að committa t.d. lykilorðum í gagnagrunn o.s.frv.
Hingað til eru 3 breytur í production_settings.py:
- DATABASES
  - Fyrir gagnagrunnsstillingar
- SECRET_KEY
  - Leyndarmál sem ætti ekki að vera opið á Github
- DEBUG
  - Af því að maður er alltaf að breyta því

### Dæmi um production_settings.py
Í Makefile er target til að búa til dæmi um production_settings.py:
```
make skolagatt/production_settings.py
```
