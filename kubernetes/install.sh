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

name=${name:-"bitlipa-api"}
nsp=${nsp:-"default"}
region_name=${region_name:-"eu-central-1"}
secret_name=${secret_name:-"arn:aws:secretsmanager:eu-central-1:931829732782:secret:bitlipa-api-secrets-Cfnp2a"}

cd $(dirname "$0")/bitlipa-api/

helm delete $name -n $nsp
helm install --set regionName=$region_name --set secretName=$secret_name $name . -n $nsp

SERVICE_IP=$(kubectl get svc --namespace $nsp $name --template "{{ range (index .status.loadBalancer.ingress 0) }}{{.}}{{ end }}")
echo "SERVICE_IP: $SERVICE_IP"
