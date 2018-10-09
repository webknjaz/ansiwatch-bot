import cherrypy

from .apps.health import HealthApp
from .web import RootBotApp


application = cherrypy.Application(RootBotApp(), '/', {})
application.root.health = HealthApp()
