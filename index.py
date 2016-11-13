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

class Main(Handler):
    def render_Main(self, list_tunes="", list_rythmes=""):
        html = self.render_str("list_tune.html", list_tunes = list_tunes, list_rythmes=list_rythmes)
        memcache.add(key="indexTune", value=html)
        self.write(html)

    def get(self):
        regenerate = self.request.get("reg")
        html = memcache.get("indexTune")
        if html is not None and regenerate != "1" and False:  
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
        if html is not None and regenerate != "1" and False:
            self.write(html)
        else:
            b_rythmes = Rythm.query()
            b_sessions = Session.query().order(Session.name_session)
            self.render_Main(b_sessions, b_rythmes)


class ViewTune(Handler):
    def render_Main(self, tune=""):
        self.render("show_tune.html", tune=tune)

    def get(self, id_tune):
        b_tunes =  Tune.query(Tune.id_tune==int(id_tune))
        if (b_tunes) :
            self.render_Main(b_tunes.get())
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
        self.response.out.write(json.dumps(tune.to_dict()))

class ApiSessions(webapp2.RequestHandler):
    def get(self):
        b_session=Session.query().order(Session.name_session)
        result = []
        for session in b_session:
            result.append(session.to_dict())
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(json.dumps(result))

class ApiRythmes(webapp2.RequestHandler):
    def get(self):
        b_rythme=Rythm.query()
        result = []
        for rythme in b_rythme:
            result.append(rythme.to_dict())
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(json.dumps(result))
        
class ApiTunesInSessions(webapp2.RequestHandler):
     def get(self):
        b_tunesInSessions=Tune_in_session.query()
        result = []
        for tunesInSession in b_tunesInSessions:
            result.append(tunesInSession.to_dict())
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(json.dumps(result))

   


app = webapp2.WSGIApplication([('/', Main),
                               ('/home/view/([^/]+)?', ViewTune),
                               ('/home/download/([^/]+)?', DownloadFile),
                               ('/home/sessions', ListSession),
                               ('/home/viewSession/([^/]+)?', ViewSession),
                               ('/api/apiTunes/([^/]+)?', ApiTunes),
                               ('/api/apiSessions', ApiSessions),
                               ('/api/apiTunesInSessions', ApiTunesInSessions),
                               ('/api/apiRythmes', ApiRythmes)],
                               debug=True)
