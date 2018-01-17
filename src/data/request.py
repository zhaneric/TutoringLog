#!/usr/bin/env python
# -*- coding: utf-8 -*-

import webapp2
from framework.main import is_debug
from google.appengine.ext import db
import csv
from data.tutor import Tutor
from data.tutee import Tutee
from google.appengine.api import users, memcache
from data.tutoring_session import TutoringSession
import json
from xhtml2pdf import pisa
from six import StringIO
from datetime import date, timedelta
import datetime


def format_minutes(time):
    if time == 0:
        return '0'
    hours = time // 60
    minutes = time % 60
    return (str(hours) + (' hours' if hours > 1 else ' hour') if hours > 0 else '') + (' ' + str(minutes) + (' minutes' if minutes > 1 else ' minute') if minutes > 0 else '')


class Request(webapp2.RequestHandler):
    @staticmethod
    def statisticsJSON(should_reload=False):
        #Retrieved cached value
        data = memcache.get('statistics')
        if data is None or should_reload:        
            summary = json.loads(Request.tutorSummaryJSON())
            
            statistics = {}
            
            statistics['members'] = len(summary)
            statistics['sessions'] = sum([entry[1] for entry in summary])
            statistics['minutes'] = sum([entry[3] for entry in summary])
            
            
            last_month = date.today() - timedelta(30)
            last_week = date.today() - timedelta(7)
            last_day = date.today() - timedelta(1)
            
            query = TutoringSession.all()
            query.filter('date_tutored >=', last_week)
            statistics['week'] = query.count(limit=10000)
            
            query.filter('date_tutored >=', last_day)
            statistics['yesterday'] = query.count(limit=10000)
            
            tutors = json.loads(Request.tutorsJSON())
            emails = [item[2] for item in tutors]
            
            statistics['none_month'] = []
            for email in emails:
                query = TutoringSession.all()
                query.filter('tutor_email =', email)
                query.filter('date_tutored >=', last_month)
                if query.count(limit=1) == 0:
                    statistics['none_month'].append(email)
                    
            statistics['top_tutor'] = [None]*3
            minutes_max = 0
            for tutor in tutors:
                email = tutor[2]
                sessions = json.loads(Request.sessionDataJSON('tutor', email))
                minutes = sum([session[7] for session in sessions])
                if minutes > minutes_max:
                    minutes_max = minutes
                    statistics['top_tutor'][0] = tutor[1] + ' ' + tutor[0]
                    statistics['top_tutor'][1] = email
                    statistics['top_tutor'][2] = minutes
                    
                    
            tutees = json.loads(Request.tuteesJSON())
            statistics['tutees'] =  len(tutees)
            
            data = json.dumps(statistics)
            memcache.add('statistics', data, 3600)
        
        return data
    
    @staticmethod
    def tutorJSONtoPDF(data):
        #If there was nothing retrieved
        if not data:
            return "No data"
        
        rows = ''
        #keys = ["tutee_name", "date_tutored", "subject", "minutes"];
        keys = [3, 6, 8, 7]
        
        entries = len(data)
        total_minutes = 0
        for i in range(0, entries):
            rows += '<tr>'
            for key in keys:
                if key == 7:
                    time = int(data[i][key])
                    rows += '<td class = "normal">' + format_minutes(time) + '</td>'
                    total_minutes += time
                else:
                    rows += '<td class = "normal">' + data[i][key] + '</td>'
            rows += '</tr>'
            
        
        with open('static/css/pdf.css', 'r') as f: css = f.read()
        
        return '''
        <html>
        <head>
        <style type = "text/css">%s</style>
        </head>
        <body>
        
        <div class = "title center">Tutoring Log</span></div>
        <div class = "label center">Mu Alpha Theta - Math Honor Society</div>
        <div class = "label center">%s %s</div>
        
        <table>
        <thead>
          <tr><td class = "head">Tutee</td><td class = "head">Date</td><td class = "head">Subject</td><td class = "head">Time</td></tr>
        </thead>
        <tbody>
        %s
        </tbody>
        </table>
        <span id = "time">Total: %s</span>
        </body>
        </html>
        ''' % (css, data[0][1], data[0][0], rows, format_minutes(total_minutes))
        
    @staticmethod
    def summaryPDF():
        statistics = json.loads(Request.statisticsJSON())
        data = json.loads(Request.tutorSummaryJSON())
        #If there was nothing retrieved
        if not data:
            return "No data"
        
        #Open the PDF stylesheet for use with XHTML to PDF.
        with open('static/css/pdf.css', 'r') as f: css = f.read()
        
        rows = ''
        rows2 = ''
        minutes = 0
        
        #Create a row with each tutor's data
        for tutor in data:
            minutes += int(tutor[3])
            
            rows += '<tr>'
            rows += '<td class = "normal">' + str(tutor[0]) + '</td>'
            rows += '<td class = "normal">' + str(tutor[1]) + '</td>'
            rows += '<td class = "normal">' + str(tutor[2]) + '</td>'
            rows += '<td class = "normal">' + format_minutes(tutor[3]) + '</td>'
            rows += '</tr>'
            
        data.sort(key = lambda x: x[3], reverse=True)
        #Create a row with each tutor's data in order of minutes
        for tutor in data:
            rows2 += '<tr>'
            rows2 += '<td class = "normal">' + str(tutor[0]) + '</td>'
            rows2 += '<td class = "normal">' + str(tutor[1]) + '</td>'
            rows2 += '<td class = "normal">' + str(tutor[2]) + '</td>'
            rows2 += '<td class = "normal">' + format_minutes(tutor[3]) + '</td>'
            rows2 += '</tr>'
        
        #Return the created XHTML to be rendered into a PDF.
        return '''
        <html>
        <head>
        <style type = "text/css">%s</style>
        </head>
        <body>
        
        <div class = "title center">Tutoring Log</span></div>
        <div class = "label center">Mu Alpha Theta - Math Honor Society</div>
        <div class = "label center">Number of club members: %d</div>
        <div class = "label center">Number of different students tutored: %d</div>
        <div class = "label center">Total time logged: %s</div>
        <div class = "label center">Total sessions logged: %d</div>
        <br/>
        <div class = "biglabel center">%s</div>
        
        <div class = "title center break">Tutoring Log</div>
        <div class = "title center">(Alphabetical Order)</div>
        <table>
        <thead>
          <tr><td class = "head">Name</td><td class = "head">Sessions</td><td class = "head">Tutees</td><td class = "head">Time</td></tr>
        </thead>
        <tbody>
        %s
        </tbody>
        </table>
        
        <div class = "title center break">Tutoring Log</div>
        <div class = "title center">(Time Order)</div>
        <table>
        <thead>
          <tr><td class = "head">Name</td><td class = "head">Sessions</td><td class = "head">Tutees</td><td class = "head">Time</td></tr>
        </thead>
        <tbody>
        %s
        </tbody>
        </table>
        </body>
        </html>
        ''' % (css, statistics['members'], statistics['tutees'], format_minutes(statistics['minutes']), statistics['sessions'], datetime.date.today().strftime('Generated %d, %B %Y'), rows, rows2)
    
    def get(self):
        if not users.is_current_user_admin():
            return
        
        ### Database queries ###
        data_query = self.request.get('data')
        if 'data' in self.request.GET:
            if data_query == 'tutor':
                if self.request.get('type') == 'csv':
                    data = json.loads(Request.sessionDataJSON('tutor', self.request.get('email')))
                    if not data:
                        self.response.out.write("No data")
                        return
                    
                    #CSV filetype / filename headers.
                    self.response.headers['Content-Type'] = 'application/csv'
                    self.response.headers['Content-Disposition'] = str('attachment; filename="' + data[0][0] + '_' + data[0][1] + '_' + data[0][2] + '.csv"')
                    
                    #Create the CSV writer
                    writer = csv.writer(self.response.out)
                    
                    head = ["Tutee Name", "Tutee Email", "Subject", "Date Tutored", "Minutes", "Satisfaction", "Comments", "ID"];
                    keys = [3,            4,             8,         6,              7,         9,              10,         11];
                    
                    writer.writerow(head)
                    entries = len(data)
                    for i in range(0, entries):
                        row = [];
                        for key in keys:
                            row.append(data[i][key])
                        writer.writerow(row)
                elif self.request.get('type') == 'pdf':
                    data = json.loads(Request.sessionDataJSON('tutor', self.request.get('email')))
                    self.response.headers['Content-Type'] = 'application/pdf'
                    output = StringIO()
                    pdf = pisa.CreatePDF(Request.tutorJSONtoPDF(data), output, encoding='utf-8')
                    pdf_data = pdf.dest.getvalue()
                    self.response.out.write(pdf_data)
                else:
                    self.response.out.write(Request.sessionDataJSON('tutor', self.request.get('email')))
                    #OLD self.response.out.write(self.tutorDataJSON(self.request.get('email'))) 
            elif data_query == 'tutee':
                if self.request.get('type') == 'csv':
                    self.response.out.write("none")
                elif self.request.get('type') == 'pdf':
                    self.response.out.write("none")
                else:
                    self.response.out.write(Request.sessionDataJSON('tutee', self.request.get('email')))
                
        if 'tutors' in self.request.GET:
            self.response.out.write(Request.tutorsJSON())
        elif 'tutees' in self.request.GET:
            self.response.out.write(Request.tuteesJSON())
        elif 'refreshtutors' in self.request.GET:
            q = db.GqlQuery("SELECT * FROM Tutor")
            for p in q.run():
                p.delete()
            tutors_file = open("static/tutors.csv", "r")
            reader = csv.reader(tutors_file)
            for line in reader:
                print line
                tutor = Tutor(last=line[0], first=line[1], email=line[2])
                tutor.put()
        elif 'summary' in self.request.GET:
            self.response.headers['Content-Type'] = 'application/pdf'
            output = StringIO()
            pdf = pisa.CreatePDF(Request.summaryPDF(), output, encoding='utf-8')
            pdf_data = pdf.dest.getvalue()
            self.response.out.write(pdf_data)
        elif 'statistics' in self.request.GET:
            self.response.out.write(Request.statisticsJSON())
    
    @staticmethod
    def tutorsJSON(should_reload=False):
        #Retrieved cached value
        data = memcache.get('tutors')
        if data is None or should_reload:
            #Load data if not cached
            query = Tutor.all()
            query.order('last')
            #Empty tutors list.
            tutors = []
            #Iterate through all the database results.
            for tutor in query.run(batch_size=200):
                #Add the tutor list data to the tutors list.
                tutors.append(tutor.to_list())
            #Create JSON string to store in memcache.
            data = json.dumps(tutors)
            #Add to cache
            memcache.add('tutors', data, 3600)
        #Return created or cached data
        return data
    
    @staticmethod
    def tuteesJSON(should_reload=False):
        #Retrieved cached value.
        data = memcache.get('tutees')
        if data is None or should_reload:
            #Load data if not cached
            query = Tutee.all()
            query.order('email')
            #Empty tutees list.
            tutees = []
            #Iterate through all the database results.
            for tutee in query.run(batch_size=400):
                #Add the tutee list data to the tutees list.
                tutees.append(tutee.to_list())
            #Create JSON string to store in memcache.
            data = json.dumps(tutees)
            #Add to cache
            memcache.add('tutees', data, 3600)
        #Return created or cached data
        return data
    
    @staticmethod
    def tutorSummaryJSON(should_reload=False):
        #Retrieved cached summary.
        data = memcache.get('summary')
        #If it does not exist or is expired, create it.
        if data is None or should_reload:
            #Get all the tutors
            tutors = json.loads(Request.tutorsJSON())
            summary = []
            # Go through each tutor
            for tutor in tutors:
                last, first, email = tutor[0], tutor[1], tutor[2]
                #Get their individual data
                tutor_data = json.loads(Request.sessionDataJSON('tutor', email, should_reload))
                
                #Default values to 0.
                minutes, sessions, tutees = 0, 0, 0
                
                #If there is data for the student, set the minutes, sessions, and tutees.
                if tutor_data:
                    minutes_list = [int(entry[7]) for entry in tutor_data] #Stored minutes into integer list
                    minutes = sum(minutes_list) #Sum for the total minutes
                    
                    #tutees_list = tutor_data['tutee_email']
                    tutees_list = [entry[2] for entry in tutor_data]  #List all the tutees emails
                    tutees = len(set(tutees_list)) #Find the length of the set of unique email
                    
                    sessions = len(minutes_list) #Number of sessions is equal to the number of entries
                
                #Add row to the summary.
                summary.append([last + ', ' + first, sessions, tutees, minutes])
            #Turn the summary into JSON data.
            data = json.dumps(summary)
            #Cache this value for 5 minutes.
            memcache.add('summary', data, 300)
        return data
    
    #TODO: fix this... dumb design choice lol
    def tutorDataJSON(self, email, should_reload=False):
        key = 'tutor_data_' + email
        data = memcache.get(key)
        if data is None or should_reload:
            print "Reloading... " + key
            q = TutoringSession.all()
            q.filter("tutor_email", email)
            q.order("date_tutored")
            compiled = {}
            for p in q.run(limit=2000):
                session_dict = p.to_dict()
                for k in session_dict.keys():
                    if not k in compiled:
                        compiled[k] = []
                    compiled[k].append(session_dict[k])
            data = json.dumps(compiled)
            memcache.add(key=key, value=data, time=300) #5 minutes per student
        return data
    
    @staticmethod
    def sessionDataJSON(which, email, should_reload=False):
        key = which + '_data_' + email
        data = memcache.get(key)
        if data is None or should_reload:
            print 'Reloading "' + key + '"'
            query = TutoringSession.all()
            query.filter(which + '_email', email)
            query.order("date_tutored")
            sessions = []
            for session in query.run(batch_size=2000):
                sessions.append(session.to_list())
            data = json.dumps(sessions)
            memcache.add(key=key, value=data, time=300) #5 minutes per student
        return data
    
    
app = webapp2.WSGIApplication([('/request', Request)], debug=is_debug())