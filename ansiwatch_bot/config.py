import cherrypy


def configure_server():
    cherrypy.config.update({'server.socket_host': '0.0.0.0'})
