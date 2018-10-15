from pathlib import Path
from warnings import catch_warnings

import cherrypy
from envparse import Env

from .request_dispatcher import GithubEventDispatcher


with catch_warnings(record=True):
    Env.read_envfile()

env = Env()


def configure_server():
    cherrypy.config.update({'server.socket_host': '0.0.0.0'})


def get_root_config():
    return {
            '/':
                {
                    'request.dispatch': GithubEventDispatcher(),
                    'tools.sessions.on': False,
                },
         }


SERVER_PORT = env('PORT', cast=int, default=8080)

# Installation integration:
APP_ID = env('GITHUB_APP_ID', cast=int)
INSTALL_ID = env('GITHUB_INSTALL_ID', cast=int, default=None)
PRIVATE_KEY_PATH = env('GITHUB_PRIVATE_KEY_PATH', default=None)
PRIVATE_KEY = env('GITHUB_PRIVATE_KEY', default=None)

# OAuth 2:
CLIENT_ID = env('GITHUB_OAUTH_CLIENT_ID')
CLIENT_SECRET = env('GITHUB_OAUTH_CLIENT_SECRET')
GH_AUTH_URL_TMPL = f'https://github.com/login/oauth/authorize?client_id={CLIENT_ID}&redirect_uri=https%3A%2F%2F{{app_domain}}%2Flogin%2Foauth'
