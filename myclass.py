
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
    id_rythme = ndb.IntProperty()
    nom_rythme = ndb.StringProperty()

class Tune(ndb.Model):
    id_tune = ndb.IntProperty()
    ref_tune = nbd.StringProperty()
    titre = ndb.StringProperty()  # name of the tune
    auteur = ndb.StringProperty()
    text_ly = ndb.StringProperty()
    image_file = ndb.StringProperty()
    pdf_file = ndb.StringProperty()
    id_rythme = ndb.IntProperty()

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
    id_rythme = ndb.IntProperty()
     
class Tune_in_session:
    id_tune = ndb.IntProperty()
    id_session = ndb.IntProperty()
    pos = ndb.IntProperty()