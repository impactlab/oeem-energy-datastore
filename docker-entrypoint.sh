#!/bin/bash

source env.sh

if [ -z "$SETUP" ]; then
	echo "Skipping setup because SETUP is unset"
else
	python manage.py migrate
	python manage.py collectstatic --noinput
fi

touch /srv/logs/gunicorn.log
touch /srv/logs/access.log
touch /srv/logs/django.log
tail -n 0 -f /srv/logs/*.log &

# exec celery multi start w1 -A oeem_energy_datastore -l info

exec gunicorn oeem_energy_datastore.wsgi \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --timeout 180 \
    --log-level=info \
    --log-file=/srv/logs/gunicorn.log \
    --access-logfile=/srv/logs/access.log \
    "$@"
