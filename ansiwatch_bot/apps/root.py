import cherrypy


class RootBotApp:
    @cherrypy.expose
    def index(self, *args, **kwargs):
        return 'Hi from ansiwatch bot index!'
