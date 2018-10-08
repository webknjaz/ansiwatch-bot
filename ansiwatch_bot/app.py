#! /usr/bin/env python
import cherrypy

from .wsgi import application


def main():
    cherrypy.tree.graft(application, '/')


__name__ == '__main__' and main()
