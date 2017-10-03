import json

from bson.objectid import ObjectId
from flask.json import JSONEncoder as encoder

from flask.ext.mysql import MySQL
from flask_login.login_manager import LoginManager
from flask_pymongo import PyMongo

lm = LoginManager()

mongo = PyMongo()
mysql = MySQL()

class MongoJSONEncoder(encoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return encoder.default(self, o)

class LoyalityJSONDecoder(json.JSONDecoder):
    def decode(self, s, **kwargs):
        result = super(LoyalityJSONDecoder, self).decode(s)
        return self._decode(result)

    def _decode(self, o):
        if isinstance(o, str) or isinstance(o, unicode):
            try:
                return int(o)
            except ValueError:
                try:
                    return float(o)
                except ValueError:
                    return o
        elif isinstance(o, dict):
            return {self._decode(k): self._decode(v) for k, v in o.items()}
        elif isinstance(o, list):
            return [self._decode(v) for v in o]
        else:
            return o