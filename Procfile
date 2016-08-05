web: gunicorn oeem_energy_datastore.wsgi --log-file -
worker: celery worker -A oeem_energy_datastore --concurrency=1
