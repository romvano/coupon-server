# -*- coding: utf-8 -*-
from bson.objectid import ObjectId
from flask_login.mixins import UserMixin
from pymongo.errors import DuplicateKeyError

from extentions import mongo
from models.host import OWNER_UID, LOYALITY_TYPE
from models.score import DB_USER_UID, DB_HOST_UID, DB_SCORE

DB_LOGIN = 'login'
DB_PASSWORD = 'password'
DB_UID = '_id'

class User(UserMixin):
    """A User model. If no login/pwd provided it fetches from db by uid"""
    def __init__(self, login=None, pwd=None, uid=None):
        if all({login, pwd}):
            self.login = login
            self.pwd = pwd
            self.uid = None
        elif uid:
            self.uid = ObjectId(uid)
            self.login = None
            self.pwd = None
            self.fetch()
        else:
            raise ValueError("Either login & pwd or uid must be provided")

    @staticmethod
    def create(login, pwd):
        """Inserts new user to db and return its uid"""
        try:
            return mongo.db.user.insert_one({
                DB_LOGIN: login,
                DB_PASSWORD: pwd,
            }).inserted_id
        except DuplicateKeyError:
            return None

    def fetch(self):
        """Updates a User model object with data from db by login and pwd or uid"""
        u = None
        if self.login:
            u = mongo.db.user.find_one({
                DB_LOGIN: self.login,
                DB_PASSWORD: self.pwd,
            })
        elif self.uid:
            u = mongo.db.user.find_one({
                DB_UID: self.uid,
            })
        if u is not None:
            self.login = u.get(DB_LOGIN)
            self.password = u.get(DB_PASSWORD)
            self.uid = u.get(DB_UID)
            return self
        return None

    def get_id(self):
        return self.uid

    def get_hosts(self):
        if not isinstance(self.uid, ObjectId):
            raise ValueError("Wrong user uid")
        scores_collection = mongo.db.score.find({DB_USER_UID: self.uid}, projection={DB_UID: False, DB_USER_UID: False})
        scores_collection = {s[DB_HOST_UID]: s[DB_SCORE] for s in scores_collection}
        host_collection = mongo.db.host.find({DB_UID: {'$in': scores_collection.keys()}})
        host_collection = {h.pop(DB_UID): h for h in host_collection}
        # score is a dict in db, there is a value for every type of lp
        for uid in host_collection:
            host_collection[uid].update({
                'score': scores_collection[uid].get(str(host_collection[uid][LOYALITY_TYPE]))
            })
        return host_collection


    def get_host_as_owner(self):
        """Soon will be DEPRECATED. Need to change for many hosts"""
        return mongo.db.host.find_one({OWNER_UID: self.uid}) or {}

    def __repr__(self):
        return '<User %s: %s' % (self.uid, self.login)
