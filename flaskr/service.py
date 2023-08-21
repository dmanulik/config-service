#!/usr/bin/env python

import base64
import json
import jsonschema
import pymongo

from flask import Flask, request, jsonify
from flask_caching import Cache
from kubernetes import client, config


with open('configuration.json') as f:
  configuration = json.load(f)

mongo_db = pymongo.MongoClient(configuration['mongo_host'], configuration['mongo_port']).configdb

config.load_incluster_config()
k8s_client = client.CoreV1Api()
redis_pass = base64.b64decode(
  k8s_client.read_namespaced_secret(
    configuration['redis_secret_name'], 
    namespace=configuration['app_namespace']
  ).data['redis-password']).decode('UTF-8')

cache_config = {
  'CACHE_TYPE': 'redis', 
  'CACHE_REDIS_HOST': configuration['redis_host'],
  'CACHE_REDIS_PORT': configuration['redis_port'],
  'CACHE_REDIS_PASSWORD': redis_pass,
  "CACHE_DEFAULT_TIMEOUT": configuration['app_cache_default_timeout']
}

def error_handler(status_code, *args):
  statuses = {
    400: {
        'message': 'Invalid config',
        'details': args[0]
    },
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
      'details': f"Please query less than {configuration['app_multiget_max_configs']}"
    }
  }
  return jsonify(statuses[status_code]), status_code


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
      return error_handler(400, e.message)
  else: 
    return error_handler(404)
  
@app.route("/get-configs")
@cache.cached(query_string=True)
def get_configs():
  config_name_list = request.args.getlist('config-name')
  config_names_string = request.args.get('configs-names')
  validation_flag = request.args.get('validate')

  # This condition provides multi-get with two options:
  # 1) get-configs?config-name=<name01>&config-name=<name02>
  # 2) get-configs?configs-names=<name01>,<name02>
  if config_names_string:
    names_list = request.args.get('configs-names').split(',')
  else:
    names_list = config_name_list 

  len_names = len(names_list)
  if len_names > configuration['app_multiget_max_configs']:
    return error_handler(422)
  else:
    app_configs = list(
        mongo_db.storage.find(
          { 'configName': { '$in': names_list } },
          { 'data': 1, '_id': 0 }
        )
      )
  
  validation_status = True
  if validation_flag:
    for app_config in app_configs:
      try:
        jsonschema.validate(app_config['data'], schema)
      except jsonschema.ValidationError as e:
        app_config['warning'] = f"Invalid config: {e.message}"
        validation_status = False

  len_app_configs = len(app_configs)
  if len_app_configs: 
    if validation_status:
      return jsonify({'configs': app_configs})
    else:
      return jsonify({'configs': app_configs}), 207
  else: 
    return error_handler(404)

@app.route("/healthz")
def healthz():
  return jsonify({'status': 200})

def put_configs():
  config_batch = []
  for config_file in configuration['app_config_files']:
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
    host=configuration['app_host'], 
    port=configuration['app_port'], 
    debug=configuration['app_debug_enabled'],
    threaded=configuration['app_threaded_enabled']
  )
