#!/bin/bash

while [ $# -gt 0 ]; do
  case "$1" in
  --name=*)
    name="${1#*=}"
    ;;
  --nsp=*)
    nsp="${1#*=}"
    ;;
  *)
    printf "***************************\n"
    printf "* Invalid argument (${1}).\n"
    printf "***************************\n"
    exit 1
    ;;
  esac
  shift
done

name=${name-"bitlipa-api"}
nsp=${nsp-"default"}

cd $(dirname "$0")/bitlipa-api/
helm upgrade $name -f values.yaml . -n $nsp

SERVICE_IP=$(kubectl get svc --namespace $nsp $name --template "{{ range (index .status.loadBalancer.ingress 0) }}{{.}}{{ end }}")
echo "SERVICE_IP: $SERVICE_IP"
