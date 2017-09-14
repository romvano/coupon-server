# -*- coding: utf-8 -*-

from flask_login.mixins import UserMixin
from pymongo.errors import DuplicateKeyError

from extentions import mongo

DB_LOGIN = 'login'
DB_PASSWORD = 'password'
DB_UID = '_id'

class User(UserMixin):
    """A User model. If no login/pwd provided it fetches from db by uid"""
    def __init__(self, login=None, pwd=None, uid=None):
        if all({login, pwd}):
            self.login = login
            self.pwd = pwd
            self.uid = uid
        elif uid:
            self.uid = uid
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

    def __repr__(self):
        return '<User %s: %s' % (self.uid, self.login)
