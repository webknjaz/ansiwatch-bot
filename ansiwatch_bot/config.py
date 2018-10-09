import cherrypy

from .request_dispatcher import GithubEventDispatcher


def configure_server():
    cherrypy.config.update({'server.socket_host': '0.0.0.0'})


def get_root_config():
    return {
            '/':
                {
                    'request.dispatch': GithubEventDispatcher(),
                },
         }

