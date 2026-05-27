#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Run the import script
python import_data.py

# Collect static files
python manage.py collectstatic --no-input