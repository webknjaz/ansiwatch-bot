#! /usr/bin/env python
import cherrypy

from .config import configure_server
from .plugins import (
    subscribe_all as subscribe_all_plugins,
)
from .wsgi import application


def main():
    cherrypy.tree.mount(application, '/', {})

    configure_server()

    subscribe_all_plugins()

    cherrypy.engine.start()
    cherrypy.engine.block()


__name__ == '__main__' and main()
