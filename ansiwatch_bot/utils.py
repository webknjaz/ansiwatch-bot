from functools import partial

import cherrypy


bus_log = partial(cherrypy.engine.publish, 'log')
