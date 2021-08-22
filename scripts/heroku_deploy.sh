#!/bin/bash

while [ $# -gt 0 ]; do
  case "$1" in
  --env=*)
    env="${1#*=}"
    ;;
  --branch=*)
    branch="${1#*=}"
    ;;
  *)
    printf "***************************\n"
    printf "* Heroku Deploy Error: Invalid argument (${1}).\n"
    printf "***************************\n"
    exit 1
    ;;
  esac
  shift
done

env=${env:-"staging"}
branch=${branch:-"HEAD:main"}

get_env_value() {
  env_variable=$(grep -w .env.${env} -e "${1}" | sed "s/${1}=//")
  env_variable=${env_variable//\'/ }
  echo $env_variable
}

if [ -f ".env.${env}" ]; then
  heroku config:set \
    DEBUG=$(get_env_value DEBUG) \
    API_URL=$(get_env_value API_URL) \
    SECRET_KEY=$(get_env_value SECRET_KEY) \
    APP_NAME=$(get_env_value APP_NAME) \
    MOBILE_APP_URL=$(get_env_value MOBILE_APP_URL) \
    MOBILE_APP_HASH=$(get_env_value MOBILE_APP_HASH) \
    THRESH0LD_API=$(get_env_value THRESH0LD_API) \
    DATABASE_URL=$(get_env_value DATABASE_URL) \
    EMAIL_HOST=$(get_env_value EMAIL_HOST) \
    EMAIL_HOST_PASSWORD=$(get_env_value EMAIL_HOST_PASSWORD) \
    EMAIL_HOST_USER=$(get_env_value EMAIL_HOST_USER) \
    EMAIL_SENDER=$(get_env_value EMAIL_SENDER) \
    TWILIO_ACCOUNT_SID=$(get_env_value TWILIO_ACCOUNT_SID) \
    TWILIO_AUTH_TOKEN=$(get_env_value TWILIO_AUTH_TOKEN) \
    TWILIO_NUMBER=$(get_env_value TWILIO_NUMBER) \
    BEYONIC_API=$(get_env_value BEYONIC_API) \
    BEYONIC_API_TOKEN=$(get_env_value BEYONIC_API_TOKEN) \
    FIXER_RAPID_API_URL=$(get_env_value FIXER_RAPID_API_URL) \
    FIXER_RAPID_API_KEY=$(get_env_value FIXER_RAPID_API_KEY) \
    FIXER_RAPID_API_HOST=$(get_env_value FIXER_RAPID_API_HOST)
fi

git push heroku-${env} ${branch}
