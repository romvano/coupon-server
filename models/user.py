# -*- coding: utf-8 -*-

from flask_login.mixins import UserMixin
from pymongo.errors import DuplicateKeyError

from extentions import mongo

DB_LOGIN = 'login'
DB_PASSWORD = 'password'
DB_UID = '_id'

class User(UserMixin):
    def __init__(self, login=None, pwd=None, uid=None):
        def init(l, p, i):
            self.login = l
            self.pwd = p
            self.uid = i

        if login is not None and pwd is not None:
            init(login, pwd, uid)
        elif uid is not None:
            u = mongo.db.user.find_one({DB_UID: uid})
            init(u.get(DB_LOGIN), u.get(DB_PASSWORD), uid)
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


    @staticmethod
    def get_by_uid(uid):
        """Creates a User object with data from db"""
        u = User(uid=uid)
        if u.login is None:
            return None
        return u

    def fetch(self):
        """Updates a User object with data from db with login and pwd"""
        u = mongo.db.user.find_one({
            DB_LOGIN: self.login,
            DB_PASSWORD: self.pwd,
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
        return '<User %d: %r' % (self.uid, self.login)
