# -*- coding: utf-8 -*-

from bson.objectid import ObjectId

from extentions import mongo
from models.host import Host

from models.__init__ import *

class Score:
    def __init__(self, host_uid, user_uid):
        self.host_uid = ObjectId(host_uid)
        self.user_uid = ObjectId(user_uid)
        self.score = None
        self.loyality_type = None
        self.fetch()

    def fetch(self):
        score = mongo.db.score.find_one({
            DB_HOST_UID: self.host_uid,
            DB_USER_UID: self.user_uid,
        })
        host = Host(uid=self.host_uid)
        if host.uid is not None:
            self.loyality_type = host.loyality_type
            if self.loyality_type not in LOYALITY_TYPES:
                raise ValueError("Loyality type in db is missen")
            if score is None or score.get('score') is None:
                self.score = 0
            else:
                self.score = score['score'].get(str(self.loyality_type), 0)

    def save(self):
        if self.loyality_type is None:
            raise ValueError("Loyality type not chosen")
        identificator = {
            DB_HOST_UID: self.host_uid,
            DB_USER_UID: self.user_uid,
        }
        data = {
            '$set': {
                '.'.join([DB_SCORE, str(self.loyality_type)]): self.score,
            }
        }
        upsert = mongo.db.score.update_one(identificator, data, upsert=True)
        if upsert.upserted_id or upsert.modified_count > 0:
            return self
        else:
            return None

    def get_discount(self):
        if self.host_uid is None:
            raise ValueError("host_uid is None")
        host = Host(self.host_uid)
        if host is None or not Host.check_loyality(host.loyality_type, host.loyality_param):
            return None
        return host.get_discount(self.score)