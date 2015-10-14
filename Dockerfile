FROM continuumio/anaconda3
ENV PYTHONUNBUFFERED 1
RUN apt-get update
RUN apt-get install -y  postgresql libpq-dev
RUN mkdir /code
WORKDIR /code
ADD requirements.txt /code/
RUN pip install -r requirements.txt
ADD . /code/

ENV DATABASE_URL postgres://postgres:@db:5432/postgres
ENV DJANGO_SETTINGS_MODULE oeem_energy_datastore.settings
ENV SECRET_KEY jalksdfk3229p0trjgoislskj

