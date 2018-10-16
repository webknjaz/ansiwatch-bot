from pathlib import Path
from warnings import catch_warnings

import cherrypy
from envparse import Env


with catch_warnings(record=True):
    Env.read_envfile()

env = Env()


def configure_server():
    cherrypy.config.update({
        'server.socket_host': '0.0.0.0',
        'server.socket_port': SERVER_PORT,
    })


def get_root_config():
    from .request_dispatcher import GithubEventDispatcher
    return {
            '/':
                {
                    'request.dispatch': GithubEventDispatcher(),
                    'tools.sessions.on': False,
                },
         }


__version__ = 0, 0, 1

SERVER_PORT = env('PORT', cast=int, default=8080)
USER_AGENT = (
    f'AnsiWatch-Bot/{".".join(map(str, __version__))}'
    f' (+https://github.com/apps/ansiwatch)'
)

# Installation integration:
APP_ID = env('GITHUB_APP_ID', cast=int)
INSTALL_ID = env('GITHUB_INSTALL_ID', cast=int, default=None)
PRIVATE_KEY_PATH = env('GITHUB_PRIVATE_KEY_PATH', default=None)
PRIVATE_KEY = env('GITHUB_PRIVATE_KEY', default=None)

# OAuth 2:
CLIENT_ID = env('GITHUB_OAUTH_CLIENT_ID')
CLIENT_SECRET = env('GITHUB_OAUTH_CLIENT_SECRET')
GH_AUTH_URL_TMPL = f'https://github.com/login/oauth/authorize?client_id={CLIENT_ID}&redirect_uri=https%3A%2F%2F{{app_domain}}%2Flogin%2Foauth'
