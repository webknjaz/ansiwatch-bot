#! /usr/bin/env python
import cherrypy

from .config import configure_server
from .wsgi import application


def main():
    cherrypy.tree.mount(application, '/', {})

    configure_server()

    cherrypy.engine.start()
    cherrypy.engine.block()


__name__ == '__main__' and main()
