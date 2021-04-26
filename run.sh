#! /usr/bin/env sh

# Run migrations
note.it db upgrade -d /app/migrations

# Execute application
exec gunicorn -k egg:meinheld#gunicorn_worker -c /app/gunicorn.conf.py noteit.wsgi:app
