#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# --- ADD THESE TWO LINES ---
# This applies the database schema and your data migrations
python manage.py migrate --noinput 

# This prepares your static files
python manage.py collectstatic --no-input
# ---------------------------