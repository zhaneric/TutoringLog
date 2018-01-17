#!/usr/bin/env python
# -*- coding: utf-8 -*-

import webapp2
from google.appengine.api import users
from framework import main
from framework.config import Configuration
from google.appengine.ext import db
from data.tutor import Tutor  # @UnusedImport for GqlQuery to detect Tutor dataclass.

class Index(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            #Automatically redirect to the appropriate page if already logged in.
            q = db.GqlQuery("SELECT * FROM Tutor WHERE email = '" + user.email() + "'")
            
            if q.count() > 0:
                self.redirect('/member')
            else:
                self.redirect('/student')
        else:
            #### HTML Start ####
            main.html_start(self)
            
            ### Head Start ###
            main.head_start(self)
            main.style_print(self, 'https://maxcdn.bootstrapcdn.com/bootstrap/3.3.5/css/bootstrap.min.css')
            main.title_set(self, 'Mu Alpha Theta – Tutoring Log – Student')
            
            main.head(self) #Common
            main.script_print(self, 'index') #Specific
            
            main.head_end(self)
            ### Head End ###
            
            ### Body Start ###
            main.body_start(self)
            
            ## Header ##
            main.html_print(self, 'header', Configuration.get_instance().title, "", "");
            ## Content ##
            main.html_print(self, 'index', Configuration.get_instance().text_student, users.create_login_url("/student"), Configuration.get_instance().text_member, users.create_login_url("/member"))
            
            main.body_end(self)
            ### Body End ###
            
            main.html_end(self)
            #### HTML End ####

app = webapp2.WSGIApplication([('/', Index)], debug=main.is_debug())