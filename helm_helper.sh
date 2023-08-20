#!/usr/bin/env bash

APP_NAME='config-service'
APP_TAG='0.1.0'

opt=$1

case $opt in
  upgrade)
    helm upgrade --install $APP_NAME helm/$APP_NAME
    ;;
  uninstall)
    helm uninstall $APP_NAME helm/$APP_NAME
    ;;
  dependency-update)
    helm dependency update helm/$APP_NAME
    ;;
  *)
    printf "ERROR: Unexpected option. \nAvaialable options: 'upgrade', 'uninstall', 'dependency-update'"
    exit 1
    ;;
esac
