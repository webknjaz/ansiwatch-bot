import cherrypy

from .apps.health import HealthApp
from .apps.root import RootBotApp
from .apps.github_events import GitHubEventHandlerApp
from .config import get_root_config


root_app_config = get_root_config()


application = cherrypy.Application(RootBotApp(), '/', root_app_config)
application.root.health = HealthApp()
application.root.gh_events = GitHubEventHandlerApp()
