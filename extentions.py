from bson.objectid import ObjectId
from flask.json import JSONEncoder as encoder

from flask.ext.mysql import MySQL
from flask_login.login_manager import LoginManager
from flask_pymongo import PyMongo

lm = LoginManager()

mongo = PyMongo()
mysql = MySQL()

def setup(m):
    m.db.user.createIndex({'login': 1}, {'unique': True})


class JSONEncoder(encoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return encoder.default(self, o)