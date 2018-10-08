import cherrypy

from .web import RootBotApp


application = cherrypy.Application(RootBotApp(), '/', {})
