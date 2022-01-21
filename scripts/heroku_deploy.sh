#!/bin/bash

while [ $# -gt 0 ]; do
  case "$1" in
  --env=*)
    env="${1#*=}"
    ;;
  --branch=*)
    branch="${1#*=}"
    ;;
  --force=*)
    force="${1#*=}"
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
branch=${branch:-"main"}

get_env_value() {
  env_variable=$(grep -w .env.${env} -e "${1}" | sed "s/${1}=//")
  env_variable=${env_variable//\'/ }
  echo "$env_variable"
}

if [ -f ".env.${env}" ]; then
  heroku config:set DEBUG=$(get_env_value DEBUG)
  heroku config:set API_URL=$(get_env_value API_URL)
  heroku config:set SECRET_KEY=$(get_env_value SECRET_KEY)
  heroku config:set APP_NAME=$(get_env_value APP_NAME)
  heroku config:set MOBILE_APP_URL=$(get_env_value MOBILE_APP_URL)
  heroku config:set MOBILE_APP_HASH=$(get_env_value MOBILE_APP_HASH)
  heroku config:set THRESH0LD_API=$(get_env_value THRESH0LD_API)
  heroku config:set DATABASE_URL=$(get_env_value DATABASE_URL)
  # # SMTP
  heroku config:set EMAIL_HOST=$(get_env_value EMAIL_HOST)
  heroku config:set EMAIL_HOST_PASSWORD=$(get_env_value EMAIL_HOST_PASSWORD)
  heroku config:set EMAIL_HOST_USER=$(get_env_value EMAIL_HOST_USER)
  heroku config:set EMAIL_SENDER=$(get_env_value EMAIL_SENDER)
  # TWILIO(SMS)
  heroku config:set TWILIO_ACCOUNT_SID=$(get_env_value TWILIO_ACCOUNT_SID)
  heroku config:set TWILIO_AUTH_TOKEN=$(get_env_value TWILIO_AUTH_TOKEN)
  heroku config:set TWILIO_NUMBER=$(get_env_value TWILIO_NUMBER)
  # BEYONIC
  heroku config:set BEYONIC_API=$(get_env_value BEYONIC_API)
  heroku config:set BEYONIC_API_TOKEN=$(get_env_value BEYONIC_API_TOKEN)
  # FIREBASE
  heroku config:set FIREBASE_SERVICE_ACCOUNT=$(get_env_value FIREBASE_SERVICE_ACCOUNT)
  # FIXER RAPID API
  heroku config:set FIXER_RAPID_API_URL=$(get_env_value FIXER_RAPID_API_URL)
  heroku config:set FIXER_RAPID_API_KEY=$(get_env_value FIXER_RAPID_API_KEY)
  heroku config:set FIXER_RAPID_API_HOST=$(get_env_value FIXER_RAPID_API_HOST)
  # ISPIRAL
  heroku config:set KYC_ISPIRAL_CLIENT_ID=$(get_env_value KYC_ISPIRAL_CLIENT_ID)
  heroku config:set KYC_ISPIRAL_CLIENT_SECRET=$(get_env_value KYC_ISPIRAL_CLIENT_SECRET)
  heroku config:set KYC_ISPIRAL_GRANT_TYPE=$(get_env_value KYC_ISPIRAL_GRANT_TYPE)
  heroku config:set KYC_ISPIRAL_API=$(get_env_value KYC_ISPIRAL_API)
  # ENIGMA
  heroku config:set ENIGMA_API_URL=$(get_env_value ENIGMA_API_URL)
  heroku config:set ENIGMA_USERNAME=$(get_env_value ENIGMA_USERNAME)
  heroku config:set ENIGMA_PASSWORD=$(get_env_value ENIGMA_PASSWORD)
fi

if [[ $force=="yes" ]] || [[ $force=="y" ]]; then
  force="-f"
else
  force=""
fi

git push heroku-${env} HEAD:${branch} ${force}
