#!/bin/bash

if [ -z "$SETUP" ]; then
	echo "Skipping setup because SETUP is unset"
else
	python manage.py migrate
	python manage.py collectstatic --noinput
fi

touch /srv/logs/gunicorn.log
touch /srv/logs/access.log
tail -n 0 -f /srv/logs/*.log &

exec gunicorn oeem_energy_datastore.wsgi \
    --bind 0.0.0.0:8000
