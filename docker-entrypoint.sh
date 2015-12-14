#!/bin/bash

export DATABASE_URL=postgres://$(cat /etc/secret-volume/pg-user):$(cat /etc/secret-volume/pg-password)@$(cat /etc/secret-volume/pg-service-name).default.svc.cluster.local:5432/$(cat /etc/secret-volume/pg-user)
export SECRET_KEY=$(cat /etc/secret-volume/secret-key)

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
