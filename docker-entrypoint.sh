#!/bin/bash

source env.sh

if [ -z "$SETUP" ]; then
	echo "Skipping setup because SETUP is unset"
else
	python manage.py migrate
	python manage.py collectstatic --noinput
fi

mkdir /srv/run/celery
mkdir /srv/logs/celery

celery multi start 3 -A oeem_energy_datastore -l info --pidfile="/srv/run/celery/%n.pid" --logfile="/srv/logs/celery/%n.log"

touch /srv/logs/gunicorn.log
touch /srv/logs/access.log
touch /srv/logs/django.log
touch /srv/logs/celery.log
tail -n 0 -f /srv/logs/*.log /srv/logs/**/*.log &

exec gunicorn oeem_energy_datastore.wsgi \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --timeout 180 \
    --log-level=info \
    --log-file=/srv/logs/gunicorn.log \
    --access-logfile=/srv/logs/access.log \
    "$@"
