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
    pip install -r dev-requirements.txt

#### Create the database

    createdb oeem_energy_datastore

#### Define the following environment variables

    export DJANGO_SETTINGS_MODULE=oeem_energy_datastore.settings
    export DATABASE_URL=postgres://:@localhost:5432/oeem_energy_datastore
    export SECRET_KEY=<django-secret-key>
    export DJANGO_LOGFILE=django.log
    export CELERY_LOGFILE=celery.log
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

Run a single test:

    py.test datastore/tests/views/test_project_run.py

#### Start a server

    python manage.py runserver

#### Connecting the datastore and the client.

Once a superuser has been created for the client and the datastore, log in
to the datastore and manually create the access token defined in the ini file.

In the admin, create a Django OAuth Toolkit application with the following
attributes:

    Client id: Use default
    User: <pick a user or create a new one>
    Redirect URI: https://example-client.openeemeter.org (this can actually be any url - we don't use it when creating an application manually)
    Client type: Confidential
    Authorization grant type: Authorization code
    Client secret: Use default
    Name: OEEM Client (can be anything that helps you remember)


Then go over and manually create a Django OAuth Toolkit access token with
the following attributes.

    User: <same user as for the application>
    Token: <any string of characters - preferably at least 30 chars long and random>
    Application: <the application you just created>
    Expires: <some future date>
    Scope: "read write" (no quotes)

The environment variable `DATASTORE_ACCESS_TOKEN` should be set to the value
of this access token in the _client_'s deployment environment. E.g.

    export DATASTORE_ACCESS_TOKEN=YOUR_TOKEN_GOES_HERE

#### Adding data

You will upload data to the datastore and view it in the client.

See the API in at this datastore URL: [http://0.0.0.0:8000/docs/](http://0.0.0.0:8000/docs/)

#### Running the meter

Once data is uploaded, you'll need to run the following management command
to actually run the meters.

    ./manage.py runmeter
