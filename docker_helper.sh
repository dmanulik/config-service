#!/usr/bin/env bash

BASE_IMAGE_TAG='3.11-slim-bookworm'
APP_NAME='config-service'
APP_TAG='0.1.0'

docker_build()
{
  docker build \
  -t "$APP_NAME" \
  --no-cache \
  --build-arg BASE_IMAGE_TAG=$BASE_IMAGE_TAG \
  -f config-service.Dockerfile .
  docker tag $APP_NAME $APP_NAME:$APP_TAG
}

opt=$1
tag=$2

case $opt in
  build)
    docker_build
    ;;
  cleanup)
    docker rm -f $APP_NAME
    docker rmi -f $(docker images $APP_NAME -a -q)
    ;;
  *)
    printf "ERROR: Unexpected option. Use 'build' or 'cleanup'"
    exit 1
    ;;
esac
