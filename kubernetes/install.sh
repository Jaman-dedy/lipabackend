#!/bin/bash

while [ $# -gt 0 ]; do
  case "$1" in
  --name=*)
    name="${1#*=}"
    ;;
  --nsp=*)
    nsp="${1#*=}"
    ;;
  --dry_run=*)
    dry_run="${1#*=}"
    ;;
  *)
    echo "***************************\n"
    echo "* Invalid argument (${1}).\n"
    echo "***************************\n"
    exit 1
    ;;
  esac
  shift
done

name=${name:-"bitlipa-api"}
nsp=${nsp:-"default"}

aws_region_name=$(grep -w $(dirname "$0")/.env -e 'AWS_REGION_NAME' | sed 's/AWS_REGION_NAME=//' | grep -v "#")
aws_access_key=$(grep -w $(dirname "$0")/.env -e 'AWS_ACCESS_KEY' | sed 's/AWS_ACCESS_KEY=//' | grep -v "#")
aws_secret_key=$(grep -w $(dirname "$0")/.env -e 'AWS_SECRET_KEY' | sed 's/AWS_SECRET_KEY=//' | grep -v "#")
aws_secret_name=$(grep -w $(dirname "$0")/.env -e 'AWS_SECRET_NAME' | sed 's/AWS_SECRET_NAME=//' | grep -v "#")

if [[ "$aws_access_key" == "" ]] || [[ "$aws_secret_key" == "" ]]; then
  echo "***************************\n"
  echo "--aws_access_key and --aws_secret_key are required"
  echo "***************************\n"
  exit 1
fi

cd $(dirname "$0")/bitlipa-api/

if [[ "$dry_run" == "y" ]] || [[ "$dry_run" == "yes" ]]; then
  helm install --dry-run \
    --set AWS_REGION_NAME=$aws_region_name \
    --set AWS_ACCESS_KEY=$aws_access_key \
    --set AWS_SECRET_KEY=$aws_secret_key \
    --set AWS_SECRET_NAME=$aws_secret_name --debug $name . -n $nsp
else
  helm delete $name -n $nsp
  helm install \
    --set AWS_REGION_NAME=$aws_region_name \
    --set AWS_ACCESS_KEY=$aws_access_key \
    --set AWS_SECRET_KEY=$aws_secret_key \
    --set AWS_SECRET_NAME=$aws_secret_name $name . -n $nsp
fi

SERVICE_IP=$(kubectl get svc --namespace $nsp $name --template "{{ range (index .status.loadBalancer.ingress 0) }}{{.}}{{ end }}")
echo "SERVICE_IP: $SERVICE_IP"
