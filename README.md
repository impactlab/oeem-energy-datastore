Open Energy Efficiency Meter Energy Datastore
=============================================

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

We recommend using virtualenv to manage python packages

    mkvirtualenv oeem-energy-datastore
    pip install -r requirements.txt

#### Create the database (and optionally the eemeter weather cache database)

    createdb oeem_energy_datastore
    createdb eemeter_weather_cache # optional

#### Define the following environment variables

    export DJANGO_SETTINGS_MODULE=oeem_energy_datastore.settings
    export DATABASE_URL=postgres://:@localhost:5432/oeem_energy_datastore
    export DJANGO_DEBUG=true
    export SECRET_KEY=############################
    export EEMETER_WEATHER_CACHE_DATABASE_URL=postgres://:@localhost:5432/eemeter_weather_cache

You might consider adding these to your virtualenv activate script

    vim /path/to/virtualenvs/oeem-energy-datastore/bin/activate
    workon oeem-energy-datastore

#### Run migrations

    python manage.py migrate

#### Create a superuser (for admin access)

    python manage.py createsuperuser

#### Run the setup script (optional)

    python manage.py setup

#### Run the tests

    py.test

#### Start a server

    python manage.py runserver
