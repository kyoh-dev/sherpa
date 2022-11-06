from psycopg2 import connect
from psycopg2.sql import SQL, Identifier

from tests.constants import TEST_TABLE


def truncate_test_table(config):
    conn = connect(**config)
    with conn:
        with conn.cursor() as cursor:
            cursor.execute(SQL("TRUNCATE TABLE {} CASCADE").format(Identifier(TEST_TABLE)))
    conn.close()
