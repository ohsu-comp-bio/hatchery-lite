import jwt
from flask import request, abort
import logging
import requests

# simulate hatchery's stateful 'launched' service

_WORKSPACES = {}

def _get_workspace(key):
    """Retrieve workspace for key."""
    return _WORKSPACES.get(key, None)


def _put_workspace(key, workspace):
    """Set workspace for key."""
    _WORKSPACES[key] = workspace


def _get_csrftoken():
    """Retrieve csrftoken from request. Used as key to state."""
    # logging.getLogger(__name__).error(request.headers)
    # logging.getLogger(__name__).error(request.cookies)
    if 'csrftoken' not in request.cookies:
        abort(403, 'No csrftoken')
    csrftoken = request.cookies.get('csrftoken')
    return csrftoken


def launch():
    """Simulates stateful workspace."""
    csrftoken = _get_csrftoken()
    _put_workspace(csrftoken, {})


def terminate():
    """Simulates stateful workspace."""
    csrftoken = _get_csrftoken()
    _put_workspace(csrftoken, None)


def proxy():
    """Simulates stateful workspace."""
    csrftoken = _get_csrftoken()
    return {'status': 'OK', 'csrftoken': csrftoken, 'workspace': _get_workspace(csrftoken)}


def status():
    """
    Simulates stateful workspace.

            status:
              type: string
              enum: [Terminating, Stopped, Launching, Running]
              description: >
                Value:
                 * `Terminating` - The workspace is shutting down
                 * `Launching` - The workspace is starting up
                 * `Stopped` - The workspace is in a failed state and must be terminated
                 * `Running` - The workspace is running and ready to be used
    """
    status = 'Unknown'
    csrftoken = _get_csrftoken()
    workspace = _get_workspace(csrftoken)
    if workspace:
        status = 'Running'
    return {'status': status}


def options():
    """
    Simulates stateful workspace.

          properties:
            name:
              type: string
              description: The display name for the container
            cpu-limit:
              type: string
              description: The CPU limit for the container
            memory-limit:
              type: string
              description: The memory limit for the container
            id:
              type: string
              description: The hash of the container, passed to /launch
    """
    csrftoken = _get_csrftoken()
    workspace = _get_workspace(csrftoken)
    if not workspace:
        abort(400, 'No workspace')

    return [{
        'name': 'foo',
        'id': 'bar',
        'cpu-limit': 'N/A',
        'memory-limit': 'N/A',
    }]



def decode_token(token):
    """Callback from connexion openapi."""
    decoded_token = jwt.decode(token, verify=False)
    return decoded_token


def auth_mapping():
    """Get resources from arborist."""
    logger = logging.getLogger(__name__)
    response = requests.get('http://arborist-service/auth/mapping', headers=request.headers)
    mapping = response.json()
    logger.warning(mapping)
    return mapping
