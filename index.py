

import webapp2
import os
import jinja2
import cgi #for escaping text
import urllib
import logging

from google.appengine.ext import ndb
from google.appengine.api import images
from google.appengine.api import users
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers


template_dir = os.path.join(os.path.dirname(__file__), 'template')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape=True)

Liste_Dance = ["Reel", "Jigs", "Hornpipe", "Song", "Mazurka", "Barndance", "Polka"]


class Tune(ndb.Model):
    name = ndb.StringProperty()  # name of the tune
    image_key = ndb.BlobKeyProperty()  # store the id of the blob contening the image
    owner_id = ndb.StringProperty()  # owner of the tune, using the id form the users api
    type_dance = ndb.StringProperty()
    image_line_key = ndb.BlobKeyProperty(repeated=True)  # store the id of the blob containing the tune on a single line

    def creat_dict(self):  # create a dictionary to be send to the jinja interpreter
        dict = {}
        dict["name"] = self.name
        dict["html"] = self.name.replace(" ","")+".html"
        dict["image_key"] = self.image_key
        dict["key"] = self.key.urlsafe()
        dict["type_dance"] = self.type_dance
        dict["image_line_key"] = self.image_line_key
        return dict


class Session(ndb.Model):
    name = ndb.StringProperty()
    tunes = ndb.StringProperty(repeated=True) 


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
            self.redirect("/listtunes")
        else:
            self.response.write("<!doctype html> <html> <p> Hello,  you aren't log in yet !You can <a href=\""
                                 + users.create_login_url(self.request.uri) +
                                 "\">sign in</a>.</p> </html>")


class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
        user = users.get_current_user()
        tuneName = self.request.get("tune_name")
        tuneType = self.request.get("type_dance")
        upload_files_full = self.get_uploads('img_full')  # 'file' is file upload field in the form
        upload_files_line = self.get_uploads('img_line')
        urlsafe_key = self.request.get("key")
        if urlsafe_key:
            key = ndb.Key(urlsafe=urlsafe_key)
            new_tune = key.get()
        else:
            new_tune = Tune()
        if upload_files_full:
            blob_info_full = upload_files_full[0]
            new_tune.image_key = blob_info_full.key()
        if upload_files_line:
            list_image = []
            for image in upload_files_line:
                list_image.append(image.key())
            new_tune.image_line_key = list_image
        new_tune.name = tuneName
        new_tune.owner_id = user.user_id()
        new_tune.type_dance = tuneType
        new_tune.put()
        self.redirect("/listtunes")


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
        self.render("list_tune.html", list_tunes = list_tunes, list_dance=Liste_Dance)

    def get(self):
        user = users.get_current_user()
        tunes = Tune.query(Tune.owner_id == user.user_id()).order(Tune.name)  
        list_tunes = []
        for tune in tunes:
            list_tunes.append(tune.creat_dict())            
        self.render_Main(list_tunes)


class ViewTune(Handler):
    def render_Main(self, key_safe, title_tune="", image_key=""):
        self.render("show_tune.html", key_safe=key_safe, title_tune=title_tune, image_key=image_key)

    def get(self, urlsafe_key):
        key = ndb.Key(urlsafe=urlsafe_key)
        tune = key.get()
        if tune:
            self.render_Main(tune.key.urlsafe(), tune.name.replace("%20"," "), tune.image_key)


class ViewPan(Handler):
    def render_Main(self, key_safe, title_tune="", image_key=""):
        self.render("view_pan.html", key_safe=key_safe, title_tune=title_tune, image_key=image_key)

    def get(self, urlsafe_key):
        key = ndb.Key(urlsafe=urlsafe_key)
        tune = key.get()
        if tune:
            self.render_Main(tune.key.urlsafe(), tune.name.replace("%20"," "), tune.image_line_key)


class AddTune(Handler):
    def render_main(self, upload_url="", tune=""):
        self.render("add_tune.html", upload_url=upload_url, list_dance=Liste_Dance, tune=tune)

    def get(self):
        urlsafe_key = self.request.get('key')
        upload_url = blobstore.create_upload_url('/upload')
        if urlsafe_key:
            key = ndb.Key(urlsafe=urlsafe_key)
            tune = key.get()
            self.render_main(upload_url, tune)
        else:
            self.render_main(upload_url)


class Logout(Handler):
    def get(self):
        self.redirect(users.create_logout_url(self.request.uri))
        
app = webapp2.WSGIApplication([('/', Main),
                               ('/listtunes', ListTune),
                               ('/tunes/([^/]+)?', ViewTune),
                               ('/view_pan/([^/]+)?', ViewPan),
                               ('/add_tune', AddTune),
                               ('/img', getImage),
                               ('/upload', UploadHandler),
                               ('/serve/([^/]+)?', ServeHandler),
                               ('/logout', Logout)],
                               debug=True)
