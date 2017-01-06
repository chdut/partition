# -*- coding: utf-8 -*-

from myclass import *
import webapp2
from google.appengine.api import taskqueue

class Main(Handler):
    def render_Main(self):
        self.render("main_util.html")

    def get(self):
        self.render_Main()

app = webapp2.WSGIApplication([('/admin/', Main)],
                               debug=True)