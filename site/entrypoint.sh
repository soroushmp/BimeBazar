#!/bin/bash

set -e

echo "Waiting for PostgreSQL to be ready..."
python << END
import os
import time
import psycopg2
from psycopg2 import OperationalError

def wait_for_postgres():
    while True:
        try:
            conn = psycopg2.connect(
                dbname=os.getenv('DB_NAME'),
                user=os.getenv('DB_USER'),
                password=os.getenv('DB_PASSWORD'),
                host=os.getenv('DB_HOST'),
                port=os.getenv('DB_PORT')
            )
            conn.close()
            print("PostgreSQL is ready!")
            break
        except OperationalError:
            print("PostgreSQL is not ready, waiting...")
            time.sleep(1)

wait_for_postgres()
END

python manage.py makemigrations
python manage.py migrate --noinput
python manage.py collectstatic --noinput
python manage.py load_initial_data
python manage.py test

exec uwsgi --ini ./uwsgi.ini