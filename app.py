#!/usr/bin/env python3
import connexion
from flask import render_template, request
from api import auth_mapping, decode_token
import logging

app = connexion.App(__name__, specification_dir='openapis/')
application = app.app # expose global WSGI application object
app.add_api('openapi.yaml')
# app.run(port=8080)


WORKSPACE_CARDS = {
    '/workspace/jupyter': {
        'title': 'jupyter',
        'description': 'Allows you to create and share documents that contain live code, equations, visualizations and narrative text.',
        'icon': '<img width="32" alt="Jupyter logo" src="https://upload.wikimedia.org/wikipedia/commons/thumb/3/38/Jupyter_logo.svg/32px-Jupyter_logo.svg.png"></img>',
        'url': '/jupyter' },
    '/workspace/kibana': {
        'title': 'kibana',
        'description': 'Provides visualization capabilities on top of the content indexed on an Elasticsearch cluster.',
        'icon': '<img width="32" alt="Kibana logo" src="https://training.elastic.co/static/images/logos/kibana-logo.svg"></img>',
        'url': '/kibana' },
    '/admin/logstash': {
        'title': 'logstash',
        'description': 'Logstash is a tool for managing events and logs, a larger system of log collection, processing, storage and searching activities.',
        'icon': '<img width="32" alt="Logstash logo" src="https://blog.frankel.ch/assets/resources/structuring-data-with-logstash/logstash.svg"></img>',
        'url': '/kibana/app/kibana?security_tenant=admin_tenant#/dashboard/c3325980-3cb7-11ea-bd69-49116f381ee3?_g=()' },

    '/workspace/hop-wiki': {
        'title': 'hop-wiki',
        'description': 'A knowledge base website on which users collaboratively modify and structure.',
        'icon': '<img width="32" alt="Wiki logo" src="https://upload.wikimedia.org/wikipedia/commons/c/c1/MediaWiki_logo_reworked_2.svg"></img>',
        'url': '/hop-wiki' },

    '/workspace/tmp': {
        'title': 'TMP',
        'description': 'Tumor molecular pathology',
        'icon': '<img width="32" alt="OHSU logo" src="https://knightdxlabs.ohsu.edu/WebsiteTemplates/KDLTemplate/App_Master/images/logo-ohsu.png"></img>',
        'url': '/tmp' },

}


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
