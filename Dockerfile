FROM continuumio/anaconda3
ENV PYTHONUNBUFFERED 1
RUN apt-get update
RUN apt-get install -y postgresql-client libpq-dev
RUN mkdir /code
WORKDIR /code
ADD requirements.txt /code/
RUN pip install -r requirements.txt
ADD . /code/

ENV DATABASE_URL postgres://django:password@postgres:5432/django
ENV DJANGO_SETTINGS_MODULE oeem_energy_datastore.settings
ENV SECRET_KEY jalksdfk3229p0trjgoislskj
ENV DJANGO_DEBUG true

CMD ["gunicorn","--bind","0.0.0.0:8000", "oeem_energy_datastore.wsgi"]
