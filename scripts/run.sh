#!/bin/bash

while [ $# -gt 0 ]; do
  case "$1" in
  --env=*)
    env="${1#*=}"
    ;;
  --port=*)
    port="${1#*=}"
    ;;
  *)
    printf "***************************\n"
    printf "* run.sh: Invalid argument (${1}).\n"
    printf "***************************\n"
    exit 1
    ;;
  esac
  shift
done

env=${env-"dev"}

if [[ $env == "staging" ]]; then
  ENV=staging python3 ./get_aws_secrets.py
fi

if [[ $env == "prod" ]] || [[ $env == "production" ]]; then
  ENV=prod python3 ./get_aws_secrets.py
fi

if [[ -f "$(dirname "$0")/../.env.$env" ]]; then
  cat $(dirname "$0")/../.env.$env >$(dirname "$0")/../.env
fi

if [[ $port == "" ]]; then
  port=$(grep -w .env -e 'PORT' | sed 's/PORT=//' | grep -v "#")
fi
if [[ $PORT ]]; then
  port=$PORT
fi

python3 manage.py migrate
python3 manage.py loaddata ./bitlipa/fixtures/*.json
python3 manage.py runapscheduler &
python3 manage.py collectstatic --noinput

if [[ $env == "prod" ]] || [[ $env == "production" ]]; then
  gunicorn bitlipa.wsgi --bind 0.0.0.0:${port:-8000} --preload --log-file -
else
  python3 manage.py runserver 0.0.0.0:${port:-8000}
fi

python3 manage.py stopapscheduler
