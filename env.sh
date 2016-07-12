#!/bin/bash

export DATABASE_URL=postgres://$(cat /etc/secret-volume/pg-user):$(cat /etc/secret-volume/pg-password)@$(cat /etc/secret-volume/pg-service-name).default.svc.cluster.local:5432/$(cat /etc/secret-volume/pg-user)
export SECRET_KEY=$(cat /etc/secret-volume/secret-key)
export DJANGO_LOGFILE=/srv/logs/django.log
export CELERY_LOGFILE=/srv/logs/celery.log
export BROKER_URL=amqp://guest:guest@$(cat /etc/secret-volume/rabbitmq-service-name).default.svc.cluster.local/
export SERVER_NAME=$(cat /etc/secret-volume/server-name)
export BROKER_TRANSPORT=amqp
export CELERY_ALWAYS_EAGER=false
export PROTOCOL=https