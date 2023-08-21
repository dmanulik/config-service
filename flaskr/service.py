#!/usr/bin/env python

import base64
import json
import jsonschema
import pymongo

from flask import Flask, request, jsonify
from flask_caching import Cache
from kubernetes import client, config


with open('configuration.json') as f:
  app_config = json.load(f)

mongo_db = pymongo.MongoClient(app_config['mongo_host'], app_config['mongo_port']).configdb

config.load_incluster_config()
k8s_client = client.CoreV1Api()
redis_pass = base64.b64decode(
  k8s_client.read_namespaced_secret(
    app_config['redis_secret_name'], 
    namespace=app_config['app_namespace']
  ).data['redis-password']).decode('UTF-8')

cache_config = {
  'CACHE_TYPE': 'redis', 
  'CACHE_REDIS_HOST': app_config['redis_host'],
  'CACHE_REDIS_PORT': app_config['redis_port'],
  'CACHE_REDIS_PASSWORD': redis_pass,
  "CACHE_DEFAULT_TIMEOUT": app_config['app_cache_default_timeout']
}

def error_handler(code):
  statuses = {
    404: {
      'message': 'No configs found',
      'details': "Please check if config name is correct" 
        "or you are using correct endpoints: "
        "'get-config?config-name=<name>', "
        "'get-configs?config-name=<name01>&config-name=<name02>', "
        "'get-configs?configs-names=<name01>,<name02>'"
    },
    422: {
      'message': 'Items limit exceeded',
      'details': f"Please query less than {app_config['app_multiget_max_configs']}"
    }
  }
  return jsonify(statuses[code]), code


app = Flask(__name__)
cache = Cache(app, config=cache_config)

with open('schema.json') as f:
  schema = json.load(f)

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
    if len_app_configs > app_config['app_multiget_max_configs']:
      return error_handler(422)
    else:
      return jsonify({'configs': app_configs})
  
  else: 
    return error_handler(404)

@app.route("/healthz")
def healthz():
  return jsonify({'status': 200})

def put_configs():
  config_batch = []
  for config_file in app_config['app_config_files']:
    with open(config_file) as f:
      file_data = json.load(f)
      config_batch.append(
        {
          'configName': file_data['name'],
          'data': file_data
        }
      )
      
  for batch in config_batch:
    query = {'configName': batch['configName']}
    newvalues = {"$set": {"data": batch['data']}}
    mongo_db.storage.update_one(
      query, 
      newvalues,
      upsert=True
    )

if __name__ == '__main__':
  put_configs()
  app.run(
    host=app_config['app_host'], 
    port=app_config['app_port'], 
    debug=app_config['app_debug_enabled'],
    threaded=app_config['app_threaded_enabled']
  )
