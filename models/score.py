# -*- coding: utf-8 -*-
import datetime
from bson.objectid import ObjectId

from extentions import mongo
from models.host import Host

from models.__init__ import *

class Score(object):

    @property
    def score(self):
        return sum(self._score.values())

    @score.setter
    def score(self, new_score):
        if new_score > self.score:
            today = datetime.datetime.now().date()
            self._score[today] = self._score.get(today, 0) + new_score - self.score
        elif new_score < self.score:
            delta = self.score - new_score
            while delta > 0:
                first_day = min(self._score.keys())
                if self._score[first_day] <= delta:
                    delta -= self._score[first_day]
                    self._score.pop(first_day)
                else:
                    self._score[first_day] -= delta
                    delta = 0

    def __init__(self, host_uid, user_uid):
        self.host_uid = ObjectId(host_uid)
        self.user_uid = ObjectId(user_uid)
        self.loyality_type = None
        self.loyality_burn = None
        self.loyality_time = 30
        self._score = None
        self.fetch()

    def fetch(self):
        score = mongo.db.score.find_one({
            DB_HOST_UID: self.host_uid,
            DB_USER_UID: self.user_uid,
        })
        host = Host(uid=self.host_uid)
        if host.uid is not None:
            self.loyality_type = host.loyality_type
            self.loyality_burn = host.loyality_burn_param
            self.loyality_time = host.loyality_time_param
            if self.loyality_type not in LOYALITY_TYPES:
                raise ValueError("Loyality type in db is missen")
            if score is None or score.get('score') is None:
                self._score = {}
            else:
                today = datetime.datetime.now().date()
                self._score = score['score'].get(str(self.loyality_type), {})
                for day in self._score:
                    self._score[datetime.datetime.strptime(day, '%Y-%m-%d').date()] = self._score.pop(day)
                # compability. Now the score will be a dict and will return computable
                if not isinstance(self._score, dict) and self._score != 0:
                    self._score = {datetime.datetime.now().date(): self.score}
                # delete all expired transactions
                if self.loyality_burn == BURN_ALL:
                    if max(self._score.keys()) < today - datetime.timedelta(self.loyality_time):
                        self._score = {}
                elif self.loyality_burn == BURN_PARTIALLY:
                    for date in self._score.keys():
                        if date < today - datetime.timedelta(self.loyality_time):
                            self._score.pop(date)
                # save if changed
                if self.loyality_burn is not None:
                    self.save()

    def save(self):
        if self.loyality_type is None:
            raise ValueError("Loyality type not chosen")
        identificator = {
            DB_HOST_UID: self.host_uid,
            DB_USER_UID: self.user_uid,
        }
        data = {
            '$set': {
                '.'.join([DB_SCORE, str(self.loyality_type)]): {day.isoformat(): val for day, val in self._score.items()},
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
        if host is None or not Host.check_loyality(host.loyality_type, host.loyality_param,
                                                   host.loyality_time_param, host.loyality_burn_param):
            return None
        return host.get_discount(self.score)