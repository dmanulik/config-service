#!/usr/bin/env bash

opt=$1

case $opt in
  bootstrap)
    printf "Step 01: Build infrastructure \n\n\n"
    ./minikube_helper.sh start
    source ./minikube_helper.sh source-docker-vars
    printf "\n\n\nStep 02: Build 'config-service' image \n\n\n"
    ./docker_helper.sh build
    printf "\n\n\nStep 03: Fetch helm dependency charts \n\n\n"
    ./helm_helper.sh dependency-update
    printf "\n\n\nStep 04: Deploy 'config-service' and initialize Mongo and Redis \n\n\n"
    ./helm_helper.sh initial-deployment
    printf "\n\n\nStep 05: Start minikube tunnel to allow endpoint access \n\n\n"
    ./minikube_helper.sh tunnel
    ;;
  shutdown)
    ./minikube_helper.sh tunnel-turnoff
    ./minikube_helper.sh delete
    source ./minikube_helper.sh unset-docker-vars
    ;;
  *)
    printf "ERROR: Unexpected option '${1}'\n"
    printf "Avaialable options: 'bootstrap', 'shutdown'"
    exit 1
    ;;
esac
