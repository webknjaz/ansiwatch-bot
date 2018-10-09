import cherrypy


class HealthApp:
    @cherrypy.expose
    def index(self):
        return "I'm ", 'okay', '!'
