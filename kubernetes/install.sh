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
echo
name=${name-"bitlipa-api"}
nsp=${nsp-"default"}

cd $(dirname "$0")/bitlipa-api/
helm delete $name -n $nsp
helm install $name . -n $nsp

SERVICE_IP=$(kubectl get svc --namespace default bitlipa-api --template "{{ range (index .status.loadBalancer.ingress 0) }}{{.}}{{ end }}")
echo "SERVICE_IP: $SERVICE_IP"
