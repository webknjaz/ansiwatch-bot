import logging

import cherrypy

from .utils import bus_log


class GithubEventDispatcher(cherrypy.dispatch.Dispatcher):
    def __call__(self, path_info):
        request = cherrypy.serving.request
        header = request.headers.get
        gh_event = header('X-GitHub-Event')

        if not gh_event:
            super().__call__(path_info)
            return

        gh_delivery = header('X-GitHub-Delivery')
        cherrypy.request.github_event = gh_event
        cherrypy.request.github_delivery = gh_delivery

        new_path_info = '/'.join((path_info.rstrip('/'), gh_event))

        bus_log(f'X-GitHub-Event: {gh_event}', logging.INFO)
        bus_log(f'X-GitHub-Delivery: {gh_delivery}', logging.INFO)

        super().__call__(new_path_info)
