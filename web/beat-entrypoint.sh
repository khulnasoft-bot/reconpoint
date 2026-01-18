#!/bin/bash

python3 manage.py check_migrations

exec "$@"
