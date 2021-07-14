#!/bin/bash

python3 manage.py collectstatic --noinput
python3 manage.py runserver ${1:-"0.0.0.0:8000"}
