

import webapp2
import os
import jinja2
import cgi #for escaping text

from google.appengine.ext import db
from google.appengine.api import images
from google.appengine.api import users

template_dir = os.path.join(os.path.dirname(__file__), 'template')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape=True)

class Tune(db.Model):
    name = db.StringProperty()
    image = db.BlobProperty()
    def creat_dict(self):
        dict = {}
        dict["name"] = self.name
        dict["url"] = self.name.replace(" ", "")+".html"
        dict["key"] = self.key()
        return dict
    
def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)
    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)
    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))
        
class getImage(webapp2.RequestHandler):
    def get(self):
        Id = self.request.get('Id_tune')
        tune = Tune.get(Id)
        if (tune and tune.image):
            self.response.headers['Content-Type'] = 'image/png'
            self.response.out.write(tune.image)
        else:
            self.error(404) 
                                
class Main(Handler):
    def render_Main(self, list_tunes=""):
        self.render("list_tune.html", list_tunes = list_tunes)
    def get(self):
        tunes = Tune.all()
        tunes.order('name')  
        list_tunes = []
        for tune in tunes :
            list_tunes.append(tune.creat_dict())            
        self.render_Main(list_tunes)

class ViewTune(Handler):
    def render_Main(self, title_tune="", Id_tune=""):
        self.render("show_tune.html", title_tune = title_tune, Id_tune=Id_tune)
    def get(self):
        key = self.request.get('Id_tune')
        name = self.request.get('title_tune')
        if key and name :
            self.render_Main(name.replace("%20"," "),key.replace("%20",""))

class AddTune(Handler):
    def render_Main(self):
        self.render("add_tune.html")
    def get(self):
        self.render_Main()
    def post(self):
        tuneName = self.request.get("tune_name")
        tuneImage = self.request.get("img")
        if tuneName and tuneImage :
            new_tune = Tune()
            new_tune.image = db.Blob(tuneImage)
            new_tune.name = tuneName
            new_tune.put()
            self.redirect("/")
        
app = webapp2.WSGIApplication([('/',Main),
                               ('/tunes', ViewTune),
                               ('/add_tune',AddTune),
                               ('/img',getImage)],
                               debug=True)
