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
  "CACHE_DEFAULT_TIMEOUT": 10
}

max_configs = 200

def error_handler(code):
  statuses = {
    404: {
      'message': 'No configs found',
      'details': "Please specify valid config name" 
        "in the form: '?config-name=<name_of_config_in_db>'"
    },
    422: {
      'message': 'Items limit exceeded',
      'details': f"Please query less than {max_configs}"
    }
  }
  return jsonify(statuses[code]), code

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
    return error_handler(404)
  
@app.route("/get-configs")
@cache.cached(query_string=True)
def get_configs():
  config_name_list = request.args.getlist('config-name')
  config_names_string = request.args.get('configs-names')
  if config_names_string:
    names_list = request.args.get('configs-names').split(',')
  else:
    names_list = config_name_list 

  app_configs = list(
      mongo_db.storage.find(
        { 'configName': { '$in': names_list } },
        { 'data': 1, '_id': 0 }
      )
    )

  len_app_configs = len(app_configs)
  if len_app_configs:
    if len_app_configs > max_configs:
      return error_handler(422)
    else:
      return jsonify({'configs': app_configs})
  
  else: 
    return error_handler(404)


@app.route("/healthz")
def healthz():
  return jsonify({'status': 200})

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=5000, debug=True)
