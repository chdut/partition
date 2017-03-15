#!/usr/bin/python
# -*- coding: utf-8 -*-

import webapp2
import jinja2
import cgi #for escaping text
import urllib
import logging
from  myclass import *
import os
import json

from google.appengine.api import images
from google.appengine.api import users
from google.appengine.api import memcache
from google.appengine.ext.webapp import blobstore_handlers

class DownloadFile(webapp2.RequestHandler):
    def get(self, pdf_file):
        file_name = self.request.get('file_name') + ".pdf"
        response = urllib.urlopen('https://tunemanager.blob.core.windows.net/mycontainer/' + pdf_file)
        html = response.read()
        self.response.headers['Content-Type'] = 'text/pdf'
        self.response.headers.add_header('content-disposition', 'attachment', filename=file_name.encode('ascii','replace'))
        self.response.out.write(html)

def delete_index_pages(id_rythme, session):
    if not session:
        memcache.delete("indexTune")
    memcache.delete("indexSession")
    memcache.delete("rythme"+str(id_rythme))

class Main(Handler):
    def render_Main(self, list_tunes="", list_rythmes=""):
        html = self.render_str("list_tune.html", list_tunes = list_tunes, list_rythmes=list_rythmes)
        memcache.add(key="indexTune", value=html)
        self.write(html)

    def get(self):
        html = memcache.get("indexTune")
        if html is not None:  
            self.write(html)
        else:           
            b_rythmes = Rythm.query()
            b_tunes =  Tune.query().order(Tune.titre)
            self.render_Main(b_tunes, b_rythmes)

class ListSession(Handler):
    def render_Main(self, list_sessions="", list_rythmes=""):
        html=self.render_str("list_sessions.html", list_sessions = list_sessions, list_rythmes=list_rythmes)
        memcache.add(key="indexSession", value=html)
        self.write(html)

    def get(self):
        regenerate = self.request.get("reg")
        html = memcache.get("indexSession")
        if html is not None:
            self.write(html)
        else:
            b_rythmes = Rythm.query()
            b_sessions = Session.query().order(Session.name_session)
            self.render_Main(b_sessions, b_rythmes)


class ViewTune(Handler):
    def render_Main(self, tune="",list_siblings=""):
        self.render("show_tune.html", tune=tune, list_siblings=list_siblings)

    def get(self, id_tune):
        b_tunes =  Tune.query(Tune.id_tune==int(id_tune))       
        if (b_tunes) :
            tune = b_tunes.get()
            list_siblings = memcache.get("rythme" + str(tune.id_rythme))
            if list_siblings is None:
                list_siblings =self.render_str('dropdown_tunes.html', list_siblings=Tune.query(projection=('id_tune', 'titre')).filter(Tune.id_rythme==tune.id_rythme).order(Tune.titre))
                memcache.add(key="rythme" + str(tune.id_rythme), value=list_siblings)
            self.render_Main(tune, list_siblings)
        else :
            self.error(404)

class ViewSession(Handler):
    def render_Main(self, session="", mytunes=""):
        self.render("show_session.html", session=session, mytunes=mytunes)

    def get(self, id_session):
        session = Session.query(Session.id_session==int(id_session))
        tune_in_session = Tune_in_session.query(Session.id_session==int(id_session)).order(Tune_in_session.pos)
        mytunes = []
        for tune in tune_in_session:
            mytunes.append(Tune.query(Tune.id_tune==tune.id_tune).get())
        if (session) :
            self.render_Main(session, mytunes)
        else :
            self.error(404)
        
class ApiTunes(webapp2.RequestHandler):
    def get(self, id_tune):
        b_tunes=Tune.query().order(Tune.titre)
        result = []
        for tune in b_tunes:
            result.append(tune.to_dict())
        self.response.headers['Content-Type'] = 'application/json'  
        self.response.out.write(json.dumps(result))

    def put(self, id_tune):
        dictionary = json.loads(self.request.body)
        tune = Tune.query(Tune.id_tune==int(id_tune)).get()
        dictionary.pop('Rythme', None)
        tune.populate(**dictionary)
        delete_index_pages(tune.id_rythme, False);
        tune.put()
    
    def post(self, id_tune):
        dictionary = json.loads(self.request.body)
        tune = Tune()
        dictionary.pop('Rythme', None)
        tune.populate(**dictionary)
        new_id = Tune().query().order(-Tune.id_tune).get().id_tune + 1
        tune.id_tune=new_id
        tune.put()
        self.response.headers['Content-Type'] = 'application/json'
        delete_index_pages(tune.id_rythme, False)
        self.response.out.write(json.dumps(tune.to_dict()))

    def delete(self, id_tune):
        tune = Tune.query(Tune.id_tune==int(id_tune)).get()
        if tune:
            tune.key.delete()

class ApiSessions(webapp2.RequestHandler):
    def get(self, id_session):
        b_session=Session.query().order(Session.name_session)
        result = []
        for session in b_session:
            result.append(session.to_dict())
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(json.dumps(result))

    def put(self, id_session):
        dictionary = json.loads(self.request.body)
        session = Session().query(Session.id_session==int(id_session)).get()
        dictionary.pop( 'Rythme', None)
        session.populate(**dictionary)
        delete_index_pages(session.id_rythme, True)
        session.put()

    def post(self, id_session):
        dictionary = json.loads(self.request.body)
        session = Session()
        dictionary.pop('Rythme', None)
        session.populate(**dictionary)
        new_id = Session().query().order(-Session.id_session).get().id_session + 1
        session.id_session = new_id
        session.put()
        self.response.headers['Content-Type'] = 'application/json'
        delete_index_pages(session.id_rythme, True);
        self.response.out.write(json.dumps(session.to_dict()))

    def delete(self, id_session):
        session = Session.query(Session.id_session==int(id_session)).get()
        if session:
            session.key.delete()

class ApiRythmes(webapp2.RequestHandler):
    def get(self):
        b_rythme=Rythm.query()
        result = []
        for rythme in b_rythme:
            result.append(rythme.to_dict())
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(json.dumps(result))
        
class ApiTunesInSessions(webapp2.RequestHandler):
    def get(self, id_session):
        b_tunesInSessions=Tune_in_session.query()
        result = []
        for tunesInSession in b_tunesInSessions:
            result.append(tunesInSession.to_dict())
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(json.dumps(result))

    def post(self, id_session):
        dictionary = json.loads(self.request.body)
        tis = Tune_in_session()
        tis.populate(**dictionary)
        tis.put()

    def delete(self, id_session):
        l_tis = Tune_in_session.query(Tune_in_session.id_session==int(id_session))
        for tis in l_tis:
           tis.key.delete()
   

class InitLocal(webapp2.RequestHandler):
    def get(self):
        b_rythme = Rythm()
        b_rythme.nom_rythme = "test"
        b_rythme.id_rythme= 1
        b_rythme.put()
        b_tune = Tune()
        b_tune.titre = "default"
        b_tune.id_tune = 1
        b_tune.id_rythme = 1
        b_tune.put()
        b_session = Session()
        b_session.name_session = "test"
        b_session.id_session = 1
        b_session.id_rythme = 1
        b_session.put()
        b_tuneInSession = Tune_in_session()
        b_tuneInSession.id_session = b_session.id_session
        b_tuneInSession.id_tune = b_tune.id_tune
        b_tuneInSession.pos = 0
        b_tuneInSession.put()

app = webapp2.WSGIApplication([('/', Main),
                               ('/home/view/([^/]+)?', ViewTune),
                               ('/home/download/([^/]+)?', DownloadFile),
                               ('/home/sessions', ListSession),
                               ('/home/viewSession/([^/]+)?', ViewSession),
                               ('/api/apiTunes/([^/]+)?', ApiTunes),
                               ('/api/apiSessions/([^/]+)?', ApiSessions),
                               ('/api/apiTunesInSessions/([^/]+)?', ApiTunesInSessions),
                               ('/api/apiRythmes', ApiRythmes),
                               ('/initlocal', InitLocal)],
                               debug=True)
