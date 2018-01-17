from google.appengine.ext import db

class Tutee(db.Model):
    email = db.StringProperty()
    name = db.StringProperty()
    
    def to_list(self):
        return [self.name, self.email]