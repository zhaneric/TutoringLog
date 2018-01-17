#!/usr/bin/env python
# -*- coding: utf-8 -*-

import webapp2
from framework.main import is_debug
from google.appengine.ext import db
from google.appengine.api import users, mail
from data.tutee import Tutee
from data.tutoring_session import TutoringSession
from datetime import datetime
from data.tutor import Tutor  # @UnusedImport for GqlQuery to detect Tutee dataclass.

data_prefix = 'data_'

class Submit(webapp2.RequestHandler):
    def post(self):
        data = {};
        for argument in self.request.arguments():
            if argument.startswith(data_prefix):
                key = argument[len(data_prefix):]
                value = self.request.get(argument)
                data[key] = value  
                #self.response.out.write(key + ': ' + value + "\n")
            
        session = TutoringSession()  
              
              
        #Tutee's name logging.        
        if data['tutee'] == "" or data['tutee'] == None:
            self.response.out.write("No student name was received. Please try again and report this error!")
            return
        else:
            #Add or update the stored name
            q = db.GqlQuery("SELECT * FROM Tutee WHERE email = '" + users.get_current_user().email() + "'")
            session.tutee_email = users.get_current_user().email()
            result = q.get()
            if result == None:
                tutee = Tutee(email=users.get_current_user().email(), name=data['tutee'])
                tutee.put()
            else:
                result.name = data['tutee']
                result.put()
                
            session.tutee_name = data['tutee']
            session.tutee_email = users.get_current_user().email()
                
        #Date tutored on and datetime logged
        session.date_logged = datetime.now()
        session.date_tutored = datetime.strptime(data['date'], '%m/%d/%Y').date()

        if data['tutor'] == users.get_current_user().email():
            self.response.out.write('Error! You cannot tutor yourself. The student must log in to their account and then select who tutored them from the list.')
            return
        
        #Tutor (club member) email, last, and first name.
        q = db.GqlQuery("SELECT * FROM Tutor WHERE email = '" + data['tutor'] + "'")
        result = q.get()
        if result == None:
            self.response.out.write("Error! Could not find the selected tutor '" + data['tutor'] + "'")
            return
        else:
            session.tutor_email = data['tutor']
            session.tutor_last = result.last
            session.tutor_first = result.first
            
        #Minutes
        if data['minutes'] == 'null' or data['minutes'] == '':
            self.response.out.write('Error! No minutes were given.')
            return
        else:
            session.minutes = int(data['minutes'])
            if session.minutes < 6:
                self.response.out.write('Error! You typed "' + str(session.minutes) +' minutes", which is very low. Surely you meant hours? Please try again with time in minutes.')
                return;
        
        #Subject
        if data['subject'] == 'null' or data['subject'] == '':
            self.response.out.write('Error! No subject was selected.')
            return
        else:
            session.subject = data['subject']
        
        #Satisfaction
        if data['satisfaction'] == 'null' or data['satisfaction'] == '':
            session.satisfaction = None
        else:
            session.satisfaction = int(data['satisfaction'])
            
        #Comments
        if data['comments'] == 'null' or data['comments'] == '':
            session.comments = None
        else:
            session.comments = data['comments']
            
        session.put()
#         self.response.out.write("Session object: " + str(vars(session)))
        self.response.out.write("Your session has been logged. Your tutor will receive a confirmation email.")


        message = mail.EmailMessage()
        if not mail.is_email_valid(session.tutor_email):
            self.response.out.write('<br/>Note, an automatic email to your tutor could not be sent. Please report this error.')
            return;

        message.sender = 'Math Tutor <mathtutor@hcrhs.org>'
        message.to = session.tutor_first + ' ' + session.tutor_last +' <' + session.tutor_email + '>'
        message.subject = 'Tutoring Session Logged'
        message.body = """
Hi %s,

%s has just logged your tutoring session.

Details:
Date: %s
Minutes: %d
Subject: %s

To view your complete log, visit tutoringlog.com
        """ % (session.tutor_first, session.tutee_name, session.date_tutored.strftime('%m/%d/%Y'), session.minutes, session.subject)

        message.send()

app = webapp2.WSGIApplication([('/submit', Submit)], debug=is_debug())