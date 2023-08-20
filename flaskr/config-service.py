#!/usr/bin/env python

import base64
import json
import jsonschema
import pymongo

from flask import Flask, request, jsonify
from flask_caching import Cache
from kubernetes import client, config

mongo_db = pymongo.MongoClient("config-service-mongodb", 27017).configdb

config.load_incluster_config()
k8s_client = client.CoreV1Api()
redis_pass = base64.b64decode(
  k8s_client.read_namespaced_secret(
    'config-service-redis', 
    namespace='default'
    ).data['redis-password']).decode('UTF-8')

with open('schema.json') as f:
  schema = json.load(f)

app = Flask(__name__)
cache_config = {
  'CACHE_TYPE': 'redis', 
  'CACHE_REDIS_HOST': 'config-service-redis-master',
  'CACHE_REDIS_PORT': 6379,
  'CACHE_REDIS_PASSWORD': redis_pass,
  "CACHE_DEFAULT_TIMEOUT": 30
}

cache = Cache(app, config=cache_config)

@app.route("/get-config")
@cache.cached(query_string=True)
def get_config():
  app_config = mongo_db.storage.find_one({'configName': request.args.get('config-name')})

  if app_config:
    try:
      jsonschema.validate(app_config['data'], schema)
      return jsonify(app_config['data'])
    except jsonschema.ValidationError as e:
      error = {
        'message': 'Invalid config',
        'details': e.message
      }
      return jsonify(error), 400
  
  else: 
    return "Please specify valid config name in the form: '?config-name=<name_of_config_in_db>'"

@app.route("/healthz")
def healthz():
  return jsonify({'status': 200})

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=5000, debug=True)
