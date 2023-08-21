#!/usr/bin/env bash

K8S_VERSION='1.27.4'
RESOURCES_CPUS='2'
RESOURCES_MEM='4g'
RESOURCES_DISK='5g'
PROFILE_NAME='config-demo-cluster'
APP_NAME='config-service'

minikube_start()
{
  minikube start \
  --profile='config-demo-cluster' \
  --kubernetes-version=$K8S_VERSION \
  --cpus=$RESOURCES_CPUS \
  --memory=$RESOURCES_MEM \
  --disk-size=$RESOURCES_DISK
}

opt=$1

case $opt in
  start)
    minikube_start
    ;;
  status)
    minikube status --profile $PROFILE_NAME
    ;;
  stop)
    minikube stop --profile $PROFILE_NAME
    ;;
  delete)
    minikube delete --profile $PROFILE_NAME
    ;;
  image-load)
    minikube image load $APP_NAME --profile $PROFILE_NAME
    ;;
  source-docker-vars)
    eval $(minikube docker-env --profile $PROFILE_NAME)
    ;;
  unset-docker-vars)
    unset $(env | grep ^DOCKER_ | sed 's/=.*//')
    ;;
  tunnel)
    minikube tunnel --profile $PROFILE_NAME
    ;;
  tunnel-turnoff)
    kill -9 $(ps -a | grep "[m]inikube_helper.sh tunnel" | awk '{print $1}') || true
    kill -9 $(ps -a | grep "[m]inikube tunnel --profile $PROFILE_NAME" | awk '{print $1}')
    ;;
  *)
    printf "ERROR: Unexpected option '${1}'\n"
    printf "Avaialable options: 'start', 'status', 'stop', 'delete', 'image-load', 'tunnel', 'tunnel-turnoff'"
    exit 1
    ;;
esac
