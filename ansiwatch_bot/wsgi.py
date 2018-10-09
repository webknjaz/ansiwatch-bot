import cherrypy

from .apps.health import HealthApp
from .apps.root import RootBotApp


application = cherrypy.Application(RootBotApp(), '/', {})
application.root.health = HealthApp()
