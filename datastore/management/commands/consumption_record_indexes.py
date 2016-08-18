
"""
Create and destroy indexes as part of loading ConsumptionRecords

Loading raw data is significantly faster if indexes and foreign key constraints are dropped and
rebuilt after importing.

This script inspects the current indexes and constraints, dropping all but the primary key
indexes.

If new indexes are added, they should be added here (not in model classes) so that they are
properly rebuilt during imports.
"""

import traceback
import string
import random
import logging
from django.core.management.base import BaseCommand
from django.db import connection
from oauth2_provider.models import get_application_model

ApplicationModel = get_application_model()

def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    if cursor is None or cursor.description is None:
        return []
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]

def execute(statement):
    cursor = connection.cursor()
    try:
        cursor.execute(statement)
        return dictfetchall(cursor)
    except:
        logging.error(traceback.print_exc())
        return None
    finally:
        cursor.close()

def get_indexes():
    # Retrieve existing indexes
    get_indexes_statement = """
        SELECT
            t.relname as table_name,
            i.relname as index_name,
            a.attname as column_name
        FROM
            pg_class t,
            pg_class i,
            pg_index ix,
            pg_attribute a
        WHERE
            t.oid = ix.indrelid
            and i.oid = ix.indexrelid
            and a.attrelid = t.oid
            and a.attnum = ANY(ix.indkey)
            and t.relkind = 'r'
            and t.relname like 'datastore_consumptionrecord'
        ORDER BY
            t.relname,
            i.relname;
    """
    return execute(get_indexes_statement)

def get_constraints():
    # Retrieve existing constraints
    get_constraints_statement = """
        SELECT
            tc.constraint_name, tc.table_name, kcu.column_name, 
            ccu.table_name AS foreign_table_name,
            ccu.column_name AS foreign_column_name 
        FROM 
            information_schema.table_constraints AS tc 
            JOIN information_schema.key_column_usage AS kcu
              ON tc.constraint_name = kcu.constraint_name
            JOIN information_schema.constraint_column_usage AS ccu
              ON ccu.constraint_name = tc.constraint_name
        WHERE constraint_type = 'FOREIGN KEY' AND tc.table_name='datastore_consumptionrecord';
    """
    return execute(get_constraints_statement)

class Command(BaseCommand):
    help = "Create and destroy indexes as part of loading ConsumptionRecords"

    def add_arguments(self, parser):
        parser.add_argument('action')

    def handle(self, *args, **options):
        action = options['action']
        assert action in ['create', 'destroy']

        actions = {
            'create': self._create,
            'destroy': self._destroy
        }[action]()

    def _destroy(self):


        drop_index_statement = """
            DROP INDEX %s
        """
        existing_indexes = get_indexes()
        for index in existing_indexes:
            if index['column_name'] != 'id':
                print('Dropping index %s' % index['index_name'])
                execute(drop_index_statement % index['index_name'])

        drop_fk_statement = """
            ALTER TABLE datastore_consumptionrecord DROP CONSTRAINT %s
        """
        existing_fks = get_constraints()
        for fk in existing_fks:
            print "Dropping constraint %s" % fk['constraint_name']
            execute(drop_fk_statement % fk['constraint_name']) 
    

    def _create(self):

        # Create an index on metadata_id if it doesn't exists
        create_metadata_id_index_statement = """
            CREATE INDEX datastore_consumptionrecord_metadata_id
            ON datastore_consumptionrecord(metadata_id)
        """

        # Create a foreign key constraint on metadata_id
        create_metadata_id_fk_statement = """
            ALTER TABLE datastore_consumptionrecord ADD CONSTRAINT
            datastore_metadata_id_fk
            FOREIGN KEY (metadata_id)
            REFERENCES datastore_consumptionmetadata(id)
            DEFERRABLE INITIALLY DEFERRED
        """

        existing_indexes = get_indexes()
        index_already_exists = any([index['column_name'] == 'metadata_id' for index in existing_indexes])

        if not index_already_exists:
            print("Creating index on metadata_id")
            execute(create_metadata_id_index_statement)
            
        existing_fks = get_constraints()
        fk_already_exists = any([fk['column_name'] == 'metadata_id' for fk in existing_fks])

        if not fk_already_exists:
            print("Create foreign key constraint")
            execute(create_metadata_id_fk_statement)

#         Indexes:
#     "datastore_consumptionrecord_pkey" PRIMARY KEY, btree (id)
#     "datastore_consumptionrecord_ffe73c23" btree (metadata_id)
# Foreign-key constraints:
#     "datast_metadata_id_53e4466e_fk_datastore_consumptionmetadata_id" FOREIGN KEY (metadata_id) REFERENCES datastore_consumptionmetadata(id) DEFERRABLE INITIALLY DEFERRED

