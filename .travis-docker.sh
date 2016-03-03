#!/bin/sh -e

echo DJANGO_SETTINGS_MODULE="$DJANGO_SETTINGS_MODULE" > env.list
echo DJANGO_LOGFILE="$DJANGO_LOGFILE" >> env.list
echo DATABASE_URL="$DATABASE_URL" >> env.list
echo PROTOCOL="$PROTOCOL" >> env.list
echo SERVER_NAME="$SERVER_NAME" >> env.list
echo BROKER_HOST="$BROKER_HOST" >> env.list
echo SECRET_KEY="$SECRET_KEY" >> env.list
echo SETUP="$SETUP" >> env.list
echo TEST="$TEST" >> env.list

docker build -t impactlab/oeem-energy-datastore .
docker run --env-file=env.list impactlab/oeem-energy-datastore
