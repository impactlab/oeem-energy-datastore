import uuid
import csv
import logging
import traceback
import re
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

from django.db import connection


def success_response():
    return ({
        "status": "success"
    }, 200)


def error_response(message="Error attempting to sync"):
    return ({
        "status": "error",
        "message": message
    }, 400)


def bulk_insert(records, fields, model_class, keys):
    """
    Insert data for the given `model_class`. Fails if any of the records throws an error.

    Parameters
    ----------
    records: list of dicts with data to insert

        Example:

        [{
            start: 2016-01-01,
            value: 10.0,
            project_id: 1
        }]

    fields: list of fields expected to import

        Example:

        ['start', 'value', 'project_id']

    model_class: Django model class

    keys: primary or composite key

        Examples:

        ['id']

        ['start', 'project_id']
    """

    if records is None or len(records) == 0:
        return success_response()

    # Error out if missing fields
    def valid_record(record):
        for field in fields:
            if field not in record:
                return False
        return True
    for record in records:
        if not valid_record(record):
            return error_response()

    tablename = model_class._meta.db_table

    cursor = connection.cursor()

    # Write the request data to an in-memory CSV file for a subsequent
    # Postgres COPY
    infile = StringIO()
    fieldnames = records[0].keys()
    writer = csv.DictWriter(infile, fieldnames=fieldnames)
    for record in records:
        writer.writerow(record)
    infile.seek(0)

    response = success_response()

    try:
        # Load data into temporary table from CSV
        cursor.copy_from(file=infile, table=tablename, sep=',',
                         columns=fieldnames, null="")
    except:
        # Log exception
        logging.error(traceback.print_exc())

        response = error_response()
    finally:
        cursor.close()

    return response
