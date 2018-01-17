from google.appengine.ext import db

class TutoringSession(db.Model):
    tutor_last = db.StringProperty()    #0
    tutor_first = db.StringProperty()   #1
    tutor_email = db.StringProperty()   #2
    
    tutee_name = db.StringProperty()    #3
    tutee_email = db.StringProperty()   #4
    
    date_logged = db.DateTimeProperty() #5
    date_tutored = db.DateProperty()    #6
    
    minutes = db.IntegerProperty()      #7
    subject = db.StringProperty()       #8
    satisfaction = db.IntegerProperty() #9
    comments = db.StringProperty()      #10
    
    #self.key().id()                    #11
    
    def to_dict(self):
        return merge_dicts(dict([(p, unicode(getattr(self, p))) for p in self.properties()]), dict([('id', self.key().id())]))
    
    def to_list(self):
        return [(item if item else 'None') for item in [self.tutor_last, self.tutor_first, self.tutor_email, self.tutee_name, self.tutee_email, unicode(self.date_logged), unicode(self.date_tutored), self.minutes, self.subject, self.satisfaction, self.comments, self.key().id()]]
    
    
def merge_dicts(x, y):
    z = x.copy()
    z.update(y)
    return z