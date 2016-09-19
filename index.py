

import webapp2
import os
import jinja2
import cgi #for escaping text
import urllib
import logging
import MySQLdb

from google.appengine.ext import ndb
from google.appengine.api import images
from google.appengine.api import users
from google.appengine.ext.webapp import blobstore_handlers


template_dir = os.path.join(os.path.dirname(__file__), 'template')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape=True)


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

        
class getImage(webapp2.RequestHandler):
    def get(self):
        Id = self.request.get('Id_tune')
        tune = Tune.get_by_id(Id)
        if tune.image:
            self.response.headers['Content-Type'] = 'image/png'
            self.response.out.write(tune.image)
        else:
            self.error(404) 

class DownloadFile(webapp2.RequestHandler):
    def get(self, pdf_file):
        file_name = self.request.get('file_name') + ".pdf"
        response = urllib.urlopen('https://tunemanager.blob.core.windows.net/mycontainer/' + pdf_file)
        html = response.read()
        self.response.headers['Content-Type'] = 'text/pdf'
        self.response.headers.add_header('content-disposition', 'attachment', filename=file_name.encode('ascii','replace'))
        self.response.out.write(html)


class Main(Handler):
    def render_Main(self, list_tunes="", list_rythmes=""):
        self.render("list_tune.html", list_tunes = list_tunes, list_rythmes=list_rythmes)

    def get(self):
        db = MySQLdb.connect(unix_socket='/cloudsql/tune-2000:us-central1:partoteque', user='root',  passwd="ETQNTtNc8qt9RuP1TK2l", db="tunemanger")
        db.query("""SELECT * FROM rythme""")
        r_db = db.store_result()
        b_rythmes = r_db.fetch_row(0,1)
        db.query("""SELECT * FROM tune ORDER BY tune.titre""")
        r_db = db.store_result()
        b_tunes = r_db.fetch_row(0,1)
        self.render_Main(b_tunes, b_rythmes)

class ListSession(Handler):
    def render_Main(self, list_sessions="", list_rythmes=""):
        self.render("list_sessions.html", list_sessions = list_sessions, list_rythmes=list_rythmes)

    def get(self):
        db =  MySQLdb.connect(unix_socket='/cloudsql/tune-2000:us-central1:partoteque', user='root',  passwd="ETQNTtNc8qt9RuP1TK2l", db="tunemanger")
        db.query("""SELECT * FROM rythme""")
        r_db = db.store_result()
        b_rythmes = r_db.fetch_row(0,1)
        db.query("""SELECT * FROM session ORDER BY session.name_session""")
        r_db = db.store_result()
        b_sessions = r_db.fetch_row(0,1)
        self.render_Main(b_sessions, b_rythmes)


class ViewTune(Handler):
    def render_Main(self, tune=""):
        self.render("show_tune.html", tune=tune)

    def get(self, id_tune):
        db = MySQLdb.connect(unix_socket='/cloudsql/tune-2000:us-central1:partoteque', user='root',  passwd="ETQNTtNc8qt9RuP1TK2l", db="tunemanger")
        db.query("SELECT * FROM tune WHERE id_tune=" + id_tune +";")
        r_db = db.store_result()
        b_tunes = r_db.fetch_row(0,1)
        if (b_tunes) :
            self.render_Main(b_tunes[0])
        else :
            self.error(404)

class ViewSession(Handler):
    def render_Main(self, session=""):
        self.render("show_session.html", session=session)

    def get(self, id_session):
        db =  MySQLdb.connect(unix_socket='/cloudsql/tune-2000:us-central1:partoteque', user='root',  passwd="ETQNTtNc8qt9RuP1TK2l", db="tunemanger")
        db.query("SELECT * FROM session WHERE id_session="+id_session +";")
        r_db = db.store_result()
        session = r_db.fetch_row(0,1)[0]
        db.query("SELECT * FROM tune JOIN tune_in_session ON tune.id_tune=tune_in_session.id_tune WHERE tune_in_session.id_session=" + id_session + ";")
        r_db = db.store_result()
        session['list_tunes'] = r_db.fetch_row(0,1)
        if (session) :
            self.render_Main(session)
        else :
            self.error(404)
        
app = webapp2.WSGIApplication([('/', Main),
                               ('/home/view/([^/]+)?', ViewTune),
                               ('/home/download/([^/]+)?', DownloadFile),
                               ('/home/sessions', ListSession),
                               ('/home/viewSession/([^/]+)?', ViewSession)],
                               debug=True)
