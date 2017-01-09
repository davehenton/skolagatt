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