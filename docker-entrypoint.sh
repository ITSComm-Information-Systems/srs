#!/usr/bin/env bash
echo entrypointer

system start nginx

set -e

python3 manage.py collectstatic --noinput
python3 manage.py migrate
python3 manage.py check --deploy

exec "${@}"
