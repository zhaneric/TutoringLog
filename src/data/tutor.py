from google.appengine.ext import db

class Tutor(db.Model):
    email = db.StringProperty()
    last = db.StringProperty()
    first = db.StringProperty()
    
    def to_dict(self):
        return dict([(p, unicode(getattr(self, p))) for p in self.properties()])
    
    def to_list(self):
        return [self.last, self.first, self.email]