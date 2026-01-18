#!/bin/bash

python3 manage.py check_migrations
python3 manage.py runserver 0.0.0.0:8000

exec "$@"
