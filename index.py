

import webapp2
import os
import jinja2
import cgi #for escaping text
import urllib

from google.appengine.ext import ndb
from google.appengine.api import images
from google.appengine.api import users
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers


template_dir = os.path.join(os.path.dirname(__file__), 'template')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape=True)

class Tune(ndb.Model):
    name = ndb.StringProperty() #name of the tune
    image_key = ndb.BlobKeyProperty() # store the id of the blob contening the image
    owner_id = ndb.StringProperty() #owner of the tune, using the id form the users api
    def creat_dict(self): #creat a dictionary to be send to the jinja interpreter
        dict = {}
        dict["name"] = self.name
        dict["html"] = self.name.replace(" ","")+".html"
        dict["image_key"]=self.image_key
        dict["key"] = self.key.id()
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
    def get_user(self):
        user = users.get_current_user()
        if user:
            self.response.headers['Content-Type'] = 'text/html'
            self.response.write('<!doctype html> <html> <p> Hello, ' + user.nickname() + "!You can <a href=\""
                                 + "/logout" +
                                 "\">sign out</a>.</p> </html>")
        else:
            self.response.write("<!doctype html> <html> <p> Hello,  you aren't log in yet !You can <a href=\""
                                 + users.create_login_url(self.request.uri) +
                                 "\">sign in</a>.</p> </html>")
            
class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):
  def post(self):
    user = users.get_current_user()
    tuneName = self.request.get("tune_name")
    upload_files = self.get_uploads('img')  # 'file' is file upload field in the form
    blob_info = upload_files[0]
    new_tune = Tune()
    new_tune.image_key = blob_info.key()
    new_tune.name = tuneName
    new_tune.owner_id=user.user_id()
    new_tune.put()
    self.redirect("/listtunes")
    #self.redirect('/serve/%s' % blob_info.key())

class ServeHandler(blobstore_handlers.BlobstoreDownloadHandler):
  def get(self, resource):
    resource = str(urllib.unquote(resource))
    blob_info = blobstore.BlobInfo.get(resource)
    self.send_blob(blob_info)

        
class getImage(webapp2.RequestHandler):
    def get(self):
        Id = self.request.get('Id_tune')
        tune = Tune.get_by_id(Id)
        if tune.image:
            self.response.headers['Content-Type'] = 'image/png'
            self.response.out.write(tune.image)
        else:
            self.error(404) 

class Main(Handler):
    def get(self):
        self.get_user()
                                        
class ListTune(Handler):
    def render_Main(self, list_tunes=""):
        self.render("list_tune.html", list_tunes = list_tunes)
    def get(self):
        user = users.get_current_user()
        tunes = Tune.query(Tune.owner_id == user.user_id()).order(Tune.name)  
        list_tunes = []
        for tune in tunes :
            list_tunes.append(tune.creat_dict())            
        self.render_Main(list_tunes)

class ViewTune(Handler):
    def render_Main(self, title_tune="", image_key=""):
        self.render("show_tune.html", title_tune = title_tune, image_key=image_key)
    def get(self):
        key = self.request.get('image_key')
        name = self.request.get('title_tune')
        if key and name :
            self.render_Main(name.replace("%20"," "),key)

class AddTune(Handler):
    def render_Main(self, upload_url=""):
        self.render("add_tune.html",upload_url=upload_url)
    def get(self):
        upload_url = blobstore.create_upload_url('/upload')
        self.render_Main(upload_url)

class Logout(Handler):
    def get(self):
        self.redirect(users.create_logout_url(self.request.uri))
        
app = webapp2.WSGIApplication([('/',Main),
                               ('/listtunes', ListTune),
                               ('/tunes', ViewTune),
                               ('/add_tune',AddTune),
                               ('/img',getImage),
                               ('/upload', UploadHandler),
                               ('/serve/([^/]+)?', ServeHandler),
                               ('/logout', Logout)],
                               debug=True)
