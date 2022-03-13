#!/bin/bash

while [ $# -gt 0 ]; do
  case "$1" in
  --region=*)
    region="${1#*=}"
    ;;
  --registry=*)
    registry="${1#*=}"
    ;;
  --image=*)
    image="${1#*=}"
    ;;
  --tag=*)
    tag="${1#*=}"
    ;;
  *)
    printf "***************************\n"
    printf "* push_docker_image_aws.sh: Invalid argument (${1}).\n"
    printf "***************************\n"
    exit 1
    ;;
  esac
  shift
done

region=${region-"eu-central-1"}
registry=${registry-"931829732782.dkr.ecr.eu-central-1.amazonaws.com"}
image=${image-"bitlipa-api"}
tag=${tag-"latest"}

aws ecr get-login-password --region $region | docker login --username AWS --password-stdin $registry

docker push $registry/$image:$tag
