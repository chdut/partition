#!/usr/bin/python
# -*- coding: utf-8 -*-

import webapp2
import jinja2
import MySQLdb
import os
from google.appengine.ext import ndb

# These environment variables are configured in app.yaml.
CLOUDSQL_CONNECTION_NAME = os.environ.get('CLOUDSQL_CONNECTION_NAME')
CLOUDSQL_USER = os.environ.get('CLOUDSQL_USER')
CLOUDSQL_PASSWORD = os.environ.get('CLOUDSQL_PASSWORD')
DEV_CONNECTION_NAME = os.environ.get('DEV_CONNECTION_NAME')
DEV_USER = os.environ.get('DEV_USER')
DEV_PASSWORD = os.environ.get('DEV_PASSWORD')


template_dir = os.path.join(os.path.dirname(__file__), 'template')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape=True)


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

def connect_to_cloudsql():
    # When deployed to App Engine, the `SERVER_SOFTWARE` environment variable
    # will be set to 'Google App Engine/version'.
    if os.getenv('SERVER_SOFTWARE', '').startswith('Google App Engine/'):
        # Connect using the unix socket located at
        # /cloudsql/cloudsql-connection-name.
        cloudsql_unix_socket = os.path.join(
            '/cloudsql', CLOUDSQL_CONNECTION_NAME)

        db = MySQLdb.connect(
            unix_socket=cloudsql_unix_socket,
            user=CLOUDSQL_USER,
            passwd=CLOUDSQL_PASSWORD)

    # If the unix socket is unavailable, then try to connect using TCP. This
    # will work if you're running a local MySQL server or using the Cloud SQL
    # proxy, for example:
    #
    #   $ cloud_sql_proxy -instances=your-connection-name=tcp:3306
    #
    else:
        db = MySQLdb.connect(
            host='localhost', user=DEV_USER, passwd=DEV_PASSWORD, db='tunemanger')

    return db

class Rythm(ndb.Model):
    id_rythme = ndb.IntegerProperty()
    nom_rythme = ndb.StringProperty()

class Tune(ndb.Model):
    id_tune = ndb.IntegerProperty()
    ref_tune = ndb.StringProperty()
    titre = ndb.StringProperty()  # name of the tune
    auteur = ndb.StringProperty()
    text_ly = ndb.TextProperty()
    image_file = ndb.StringProperty()
    pdf_file = ndb.StringProperty()
    id_rythme = ndb.IntegerProperty()

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
    name_session = ndb.StringProperty()
    image_session=ndb.StringProperty()
    pdf_session = ndb.StringProperty()
    id_rythme = ndb.IntegerProperty()
    id_session = ndb.IntegerProperty()
     
class Tune_in_session(ndb.Model):
    id_tune = ndb.IntegerProperty()
    id_session = ndb.IntegerProperty()
    pos = ndb.IntegerProperty()