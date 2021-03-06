define PRODUCTION_SETTINGS
ALLOWED_HOSTS = ['localhost']
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'skolagatt',
        'USER': 'postgres',  # Postgres user that has all privileges for the skolagatt DB
        'PASSWORD': '',  # Password for Postgres user
        'HOST': 'localhost',  # Address of postgres server, defaults to localhost (for dev)
        'PORT': '5432',
    }
}

SECRET_KEY = 'k+&1)2^g5^a*4nl+vlz)_ezv8!bup(ttn0(byvm)(gx%&c)w-5'

DEBUG = True
CELERY_RESULT_BACKEND = "db+postgresql+psycopg2://user:password@localhost:5432/skolagatt"
endef

export PRODUCTION_SETTINGS

skolagatt/production_settings.py:
	@echo "$$PRODUCTION_SETTINGS" > skolagatt/production_settings.py

check:
	( \
		source venv/bin/activate; \
		pep8 -v; \
	)

venv: venv/bin/activate

venv/bin/activate: requirements.txt
	test -d venv || virtualenv venv
	venv/bin/pip install -Ur requirements.txt
	touch venv/bin/activate

test: venv skolagatt/production_settings.py clearmigrations
	( \
		source venv/bin/activate; \
		./manage.py collectstatic --no-input; \
		./manage.py test -v 2; \
	)

travis-test: skolagatt/production_settings.py 
	find ~/virtualenv/ -name "migrations" -type d | grep -v "site-packages\/django\/db\/migrations" | xargs rm -rf
	pep8 -v
	./manage.py collectstatic --no-input
	coverage run ./manage.py test -v 2
	coverage xml
	./cc-test-reporter after-build -t coverage.py || true

genfixtures: venv skolagatt/production_settings.py
	./manage.py dumpdata auth.user --format=json --indent=4 --natural-foreign > common/fixtures/auth.json
	./manage.py dumpdata common --format=json --indent=4 --natural-foreign > common/fixtures/common.json

clean:
	find . -name "*.pyc" | xargs rm -f

clearmigrations:
	find . -name "migrations" -type d | grep -v "site-packages\/django\/db\/migrations" | xargs rm -rf 
