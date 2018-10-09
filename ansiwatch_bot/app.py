#! /usr/bin/env python
import cherrypy

from .wsgi import application


def main():
    cherrypy.tree.mount(application, '/', {})

    cherrypy.engine.start()
    cherrypy.engine.block()


__name__ == '__main__' and main()
