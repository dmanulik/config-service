#!/usr/bin/env bash

set -x

curl -IL "http://127.0.0.1:5055/get-configs?config-name=test-config-1"
curl -IL "http://127.0.0.1:5055/get-configs?config-name=test-config-1&config-name=test-config-2"
curl -IL "http://127.0.0.1:5055/get-configs?configs-names=test-config-1,test-config-2"
curl -IL "http://127.0.0.1:5055/get-configs?configs-names=test-config-1,test-config-2&validate=true"
curl -IL "http://127.0.0.1:5055/get-configs?configs-names=test-config-1,test-config-2,test-config-3,test-config-4,test-config-5"


curl "http://127.0.0.1:5055/get-configs?config-name=test-config-1"
curl "http://127.0.0.1:5055/get-configs?config-name=test-config-1&config-name=test-config-2"
curl "http://127.0.0.1:5055/get-configs?configs-names=test-config-1,test-config-2"
curl "http://127.0.0.1:5055/get-configs?configs-names=test-config-1,test-config-2&validate=true"
curl "http://127.0.0.1:5055/get-configs?configs-names=test-config-1,test-config-2,test-config-3,test-config-4,test-config-5"
