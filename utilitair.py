# -*- coding: utf-8 -*-

from myclass import *
import webapp2
from google.appengine.api import taskqueue

class Main(Handler):
    def render_Main(self):
        self.render("main_util.html")

    def get(self):
        self.render_Main()

class Rythme_tonsql(webapp2.RequestHandler):
    def get(self):
        db = connect_to_cloudsql()
        db.query("""SELECT * FROM rythme""")
        r_db = db.store_result()
        b_rythmes = r_db.fetch_row(0,1)
        for rythme in b_rythmes:
            my_rythme = Rythm(id_rythme=rythme["id_rythme"], nom_rythme=rythme["nom_rythme"])
            my_rythme.put()
        self.redirect("/admin/")

class Tune_tonsql(webapp2.RequestHandler):
    def get(self):
        db = connect_to_cloudsql()
        db.query("""SELECT * FROM tune""")
        r_db = db.store_result()
        b_tunes = r_db.fetch_row(0,1)
        for tune in b_tunes:
            my_tune= Tune(id_tune=tune["id_tune"], titre=tune["titre"], auteur=tune["auteur"], id_rythme=tune["id_rythme"], ref_tune=tune["ref_tune"], text_ly=tune["text_ly"], image_file=tune["image_file"], pdf_file=tune["pdf_file"])
            my_tune.put()
        self.redirect("/admin/")

class Session_tonsql(webapp2.RequestHandler):
    def get(self):
        db = connect_to_cloudsql()
        db.query("""SELECT * FROM session""")
        r_db = db.store_result()
        b_sessions = r_db.fetch_row(0,1)
        for session in b_sessions:
            my_session= Session(id_session=session["id_session"], name_session=session["name_session"], image_session=session["image_session"], pdf_session=session["pdf_session"], id_rythme=session["id_rythme"])
            my_session.put()
        self.redirect("/admin/")

class Tune_in_session_tonsql(webapp2.RequestHandler):
    def get(self):
        db = connect_to_cloudsql()
        db.query("""SELECT * FROM tune_in_session""")
        r_db = db.store_result()
        b_tunes_in_session = r_db.fetch_row(0,1)
        for tune in b_tunes_in_session:
            my_tune= Tune_in_session(id_tune=tune["id_tune"], id_session=tune["id_session"], pos=tune["pos"])
            my_tune.put()
        self.redirect("/admin/")

app = webapp2.WSGIApplication([('/admin/', Main),
                                ("/admin/rythme_mysql_to_nosql", Rythme_tonsql),
                                ("/admin/tune_mysql_to_nosql", Tune_tonsql),
                                ("/admin/session_mysql_to_nosql", Session_tonsql),
                                ("/admin/tune_in_session_mysql_to_nosql", Tune_in_session_tonsql)],
                               debug=True)