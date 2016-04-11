FROM continuumio/anaconda3

ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y postgresql-client libpq-dev

EXPOSE 8000

ENV DJANGO_SETTINGS_MODULE oeem_energy_datastore.settings
ENV STATIC_ROOT /srv/static

RUN mkdir /srv/static /srv/logs /srv/run

VOLUME /srv/static

RUN mkdir /code
WORKDIR /code
ADD requirements.txt /code/
RUN conda install pandas=0.18.0
RUN pip install -r requirements.txt
ADD . /code/

COPY ./docker-entrypoint.sh /
ENTRYPOINT ["/docker-entrypoint.sh"]
