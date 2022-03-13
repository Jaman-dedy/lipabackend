#!/bin/bash

while [ $# -gt 0 ]; do
  case "$1" in
  --name=*)
    name="${1#*=}"
    ;;
  --region=*)
    region="${1#*=}"
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

name=${name-"bitlipa"}
region=${region-"eu-central-1"}

eksctl delete cluster --name $name --region $region
eksctl create cluster -f eks_cluster.yaml
aws eks --region $region update-kubeconfig --name $name
