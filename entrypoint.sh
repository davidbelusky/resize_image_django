#!/bin/sh


python manage.py migrate --no-input
python manage.py collectstatic --no-input

#gunicorn wsgi:application --timeout 60 --bind 0.0.0.0:8000
python manage.py runserver 0.0.0.0:8000