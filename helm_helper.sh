#!/usr/bin/env bash

APP_NAME='config-service'
APP_TAG='0.1.0'

upgrade_app()
{
  helm upgrade --install $APP_NAME helm/$APP_NAME
}

initial_deployment()
{
  REDIS_PASSWORD=$(openssl rand -base64 32)
  MONGODB_ROOT_PASSWORD=$(openssl rand -base64 32)
  upgrade_app \
  --set redis.auth.password=$REDIS_PASSWORD \
  --set auth.rootPassword=$MONGODB_ROOT_PASSWORD
}

opt=$1

case $opt in
  upgrade)
    upgrade_app
    ;;
  uninstall)
    helm uninstall $APP_NAME helm/$APP_NAME
    ;;
  dependency-update)
    helm dependency update helm/$APP_NAME
    ;;
  initial-deployment)
    initial_deployment
    ;;
  *)
    printf "ERROR: Unexpected option '${1}'\n"
    printf "Avaialable options: 'upgrade', 'uninstall', 'dependency-update', 'initial-deployment'"
    exit 1
    ;;
esac
