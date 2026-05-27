#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt

# This is the critical line that triggers your migration
python manage.py migrate --noinput 

python manage.py collectstatic --no-input