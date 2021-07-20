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

git push heroku-${env} ${branch}
