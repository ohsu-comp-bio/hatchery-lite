#!/usr/bin/env python3
import connexion
from flask import render_template, request, jsonify, current_app
from api import auth_mapping, decode_token
import logging
import yaml


WORKSPACE_CARDS = {}


def read_config():
    global WORKSPACE_CARDS 
    with open('workspace_cards.yaml', 'r') as stream:
        try:
            WORKSPACE_CARDS = yaml.safe_load(stream)
            print(WORKSPACE_CARDS)
        except yaml.YAMLError as exc:
            print(exc)

app = connexion.App(__name__, specification_dir='openapis/')
application = app.app # expose global WSGI application object
app.add_api('openapi.yaml')
read_config()

# app.run(port=8080)


@app.route('/reload')
def reload():
    read_config()
    current_app.logger.warn(WORKSPACE_CARDS)
    return jsonify(list(WORKSPACE_CARDS.keys()))


@app.route('/')
def workspace_chooser():
    access_token = extract_access_token(request)
    access_token = decode_token(access_token)
    current_user = access_token['context']['user']['name']
    users_mapping = {}
    for key, mapping_list in auth_mapping().items():
        if key in WORKSPACE_CARDS:
            mapping_list[0].update(WORKSPACE_CARDS[key])
            users_mapping[key] = [mapping_list[0]]
    return render_template('workspace_chooser.html', name=current_user, auth_mapping=users_mapping)


def extract_access_token(r):
    access_token = None
    logger = logging.getLogger(__name__)
    if 'Authorization' in request.headers:
        authorization = r.headers.get('Authorization')
        logger.warning('Authorization in header')
        authorization = authorization.split(' ')
        if len(authorization) != 2:
            logger.warning('len(authorization) != 2')
            return abort(401)
        if authorization[0].lower() != 'bearer':
            logger.warning('no bearer')
            return abort(401)
        access_token = authorization[1]
    elif 'access_token' in r.cookies:
        access_token = r.cookies.get('access_token')
        logger.warning('access_token in header')
    if not access_token:
        logger.warning('No access token found in cookie or header')
        return abort(401, "No access token found in cookie or header")
    return access_token
