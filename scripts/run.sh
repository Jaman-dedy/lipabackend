#!/bin/bash

python3 manage.py migrate
python3 manage.py runapscheduler &
python3 manage.py collectstatic --noinput
python3 manage.py runserver ${1:-"0.0.0.0:8000"}
python3 manage.py stopapscheduler
