#! /usr/bin/env python
import cherrypy

from .wsgi import application


def main():
    cherrypy.tree.graft(raw_wsgi_app, '/')


__name__ == '__main__' and main()
