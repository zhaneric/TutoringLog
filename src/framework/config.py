import datetime
from google.appengine.ext import db
import yaml


fields = ['title', 'text_student', 'text_member']

class Configuration(db.Model):
    CACHE_TIME = datetime.timedelta(minutes=1)
    
    title = db.StringProperty()
    text_student = db.StringProperty()
    text_member = db.StringProperty()
    
    _INSTANCE = None
    _INSTANCE_AGE = None
    
    @classmethod
    def get_instance(cls):
        now = datetime.datetime.now()
        if not cls._INSTANCE or cls._INSTANCE_AGE + cls.CACHE_TIME < now:
            cls._INSTANCE = cls.get_or_insert('config')
            cls._INSTANCE_AGE = now
            
            with open("config.yaml", 'r') as stream:
                print("Loading config...")
                data = yaml.load(stream)
                
                changed = False
                #Load defaults...
                for field in fields:
                    if getattr(cls._INSTANCE, field) == None:
                        setattr(cls._INSTANCE, field, data[field])
                        changed = True
                        
                if changed: 
                    cls._INSTANCE.put()
            
        return cls._INSTANCE