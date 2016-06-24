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

def bulk_sync(records, fields, model_class, keys):
    """
    Upsert data for the given `model_class` using a temporary table.

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

    # Build schema from field names
    schema = [
        {
            'name': field,
            'type': model_class._meta.get_field(field).db_type(connection)
        }
        for field in fields
    ]

    # Bulk upsert, using (start, metadata_id) as primary key
    cursor = connection.cursor()

    # Create temporary table
    tmp_id = re.sub("-", "", str(uuid.uuid4()))
    tablename = model_class._meta.db_table
    tmp_tablename = "tmp_" + tablename + "_" + tmp_id

    schema_statement = ",".join([
      column['name'] + " " + column['type'] for column in schema
    ])

    create_tmp_table_statement = """
      CREATE TEMPORARY TABLE {tmp_tablename}({schema_statement});
    """.format(tmp_tablename=tmp_tablename, schema_statement=schema_statement)

    # Write the request data to an in-memory CSV file for a subsequent Postgres COPY
    infile = StringIO()
    fieldnames = records[0].keys()
    writer = csv.DictWriter(infile, fieldnames=fieldnames)
    for record in records:
        writer.writerow(record)
    infile.seek(0)

    # Build SQL statement for upsert from temporary table to real table
    update_schema_statement = ",".join([
      "{name} = {tmp_tablename}.{name}".format(name=column['name'], tmp_tablename=tmp_tablename) for column in schema
    ])

    insert_columns = ",".join([
      column['name'] for column in schema
    ])

    insert_schema_statement = ",".join([
      "{tmp_tablename}.{name}".format(name=column['name'], tmp_tablename=tmp_tablename) for column in schema
    ])

    key_statement = " AND ".join([
        "{tablename}.{key} = {tmp_tablename}.{key}".format(tablename=tablename, tmp_tablename=tmp_tablename, key=key)
        for key in keys
    ])

    where_statement = " AND ".join([
        "{tablename}.{key} IS NULL".format(tablename=tablename, key=key)
        for key in keys
    ])

    upsert_statement = """
      UPDATE {tablename}
      SET {update_schema_statement}
      FROM {tmp_tablename}
      WHERE {key_statement};

      INSERT INTO {tablename}({insert_columns})
      SELECT {insert_schema_statement}
      FROM {tmp_tablename}
      LEFT OUTER JOIN {tablename} ON {key_statement}
      WHERE {where_statement};
    """.format(tablename=tablename,
               tmp_tablename=tmp_tablename,
               key_statement=key_statement,
               where_statement=where_statement,
               update_schema_statement=update_schema_statement,
               insert_columns=insert_columns,
               insert_schema_statement=insert_schema_statement)

    response = success_response()

    try:
        # Create the temporary table
        cursor.execute(create_tmp_table_statement)

        # Load data into temporary table from CSV
        cursor.copy_from(file=infile, table=tmp_tablename, sep=',', columns=fieldnames)

        # Upsert it into the actual table
        cursor.execute(upsert_statement)
    except:
        # Log exception
        logging.error(traceback.print_exc())

        response = error_response()
    finally:
        cursor.close()

    return response
