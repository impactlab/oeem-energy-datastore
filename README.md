Open Energy Efficiency Meter Energy Datastore
=============================================

[![Build Status](https://travis-ci.org/impactlab/oeem-energy-datastore.svg?branch=develop)](https://travis-ci.org/impactlab/oeem-energy-datastore)

This datastore app provides an API for storing consumption data, project data,
and reading meter run data. It is an OAuth 2 provider.

Setup
-----

#### Make sure OS level dependencies are installed

- postgres

#### Clone the repo & change directories

    git clone git@github.com:impactlab/oeem-energy-datastore.git
    cd oeem-energy-datastore

#### Install required python packages

We recommend using virtualenv (or virtualenvwrapper) to manage python packages

    mkvirtualenv oeem-energy-datastore
    pip install -r requirements.txt

#### Create the database

    createdb oeem_energy_datastore

#### Define the following environment variables

    export DJANGO_SETTINGS_MODULE=oeem_energy_datastore.settings
    export DATABASE_URL=postgres://:@localhost:5432/oeem_energy_datastore
    export SECRET_KEY=<django-secret-key>
    export DJANGO_LOGFILE=django.log
    export BROKER_HOST=0.0.0.0:5672 # Placeholder (not currently used - can be any valid URI)

    # For development only
    export DEBUG=true

    # for API docs
    export SERVER_NAME=0.0.0.0:8000 # the IP or DNS name where datastore will be deployed
    export PROTOCOL=http

You might consider adding these to your virtualenv postactivate script

    vim /path/to/virtualenv/oeem-energy-datastore/bin/postactivate

    # refresh environment
    workon oeem-energy-datastore

#### Run migrations

    python manage.py migrate

#### Create a superuser (for admin access)

    python manage.py createsuperuser

#### Run the tests

    py.test

#### Start a server

    python manage.py runserver
