import cherrypy


@cherrypy.tools.register('before_handler', priority=30)
def json_to_args():
    request = cherrypy.serving.request
    request.handler._kwargs.update(request.json)
