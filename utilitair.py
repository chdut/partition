import myclass
import webapp2

class Main(myclass.Handler):
    def render_Main(self):
        self.render("main_util.html")

    def get(self):
        self.render_Main()

app = webapp2.WSGIApplication([('/admin/', Main)],
                               debug=True)