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
  eval $(minikube docker-env --profile $PROFILE_NAME)
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
    unset $(env | grep ^DOCKER_ | sed 's/=.*//')
    ;;
  image-load)
    minikube image load $APP_NAME
    ;;
  *)
    printf "ERROR: Unexpected option. \nAvaialable options: 'start', 'status', 'stop', 'delete'"
    exit 1
    ;;
esac


#--driver='qemu2' \
#--container-runtime='containerd' \