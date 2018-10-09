import logging

import cherrypy

from ..utils import bus_log


@cherrypy.tools.json_in()
class GitHubEventHandlerApp:
    @cherrypy.tools.json_in()
    @cherrypy.expose
    def ping(self):
        app_id = cherrypy.request.json["hook"]["app_id"]
        zen = cherrypy.request.json["zen"]
        bus_log(f'App ID: {app_id}', logging.INFO)
        bus_log(f'Zen: {zen}', logging.INFO)
        return zen
        # raise cherrypy.HTTPError(204, zen)
