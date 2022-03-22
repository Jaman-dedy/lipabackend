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

aws_region_name=$(grep -w $(dirname "$0")/.env -e 'AWS_REGION_NAME' | sed 's/AWS_REGION_NAME=//' | grep -v "#")
aws_access_key=$(grep -w $(dirname "$0")/.env -e 'AWS_ACCESS_KEY' | sed 's/AWS_ACCESS_KEY=//' | grep -v "#")
aws_secret_key=$(grep -w $(dirname "$0")/.env -e 'AWS_SECRET_KEY' | sed 's/AWS_SECRET_KEY=//' | grep -v "#")
aws_secret_name=$(grep -w $(dirname "$0")/.env -e 'AWS_SECRET_NAME' | sed 's/AWS_SECRET_NAME=//' | grep -v "#")

cd $(dirname "$0")/bitlipa-api/
# helm upgrade $name -f values.yaml . -n $nsp

if [[ "$dry_run" == "y" ]] || [[ "$dry_run" == "yes" ]]; then
  helm upgrade --dry-run \
    --set AWS_REGION_NAME=$aws_region_name \
    --set AWS_ACCESS_KEY=$aws_access_key \
    --set AWS_SECRET_KEY=$aws_secret_key \
    --set AWS_SECRET_NAME=$aws_secret_name --debug $name -f values.yaml . -n $nsp
else
  helm upgrade \
    --set AWS_REGION_NAME=$aws_region_name \
    --set AWS_ACCESS_KEY=$aws_access_key \
    --set AWS_SECRET_KEY=$aws_secret_key \
    --set AWS_SECRET_NAME=$aws_secret_name $name -f values.yaml . -n $nsp
fi

SERVICE_IP=$(kubectl get svc --namespace $nsp $name --template "{{ range (index .status.loadBalancer.ingress 0) }}{{.}}{{ end }}")
echo "SERVICE_IP: $SERVICE_IP"
