# -*- coding: utf-8 -*-

import re

from __builtin__ import unicode
from bson.objectid import ObjectId
from flask_login.mixins import UserMixin
from pymongo.errors import DuplicateKeyError

from extentions import mongo
from models.__init__ import *

class User(UserMixin):
    """A User model. If no login/pwd provided it fetches from db by uid"""
    def __init__(self, login=None, pwd=None, uid=None):
        if all({login, pwd}):
            self.login = login
            self.pwd = pwd
            self.uid = None
            self.workplace_uid = None
        elif uid:
            self.uid = ObjectId(uid)
            self.login = None
            self.pwd = None
            self.workplace_uid = None
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
            self.workplace_uid = u.get(DB_WORKPLACE)
            self.uid = u.get(DB_UID)
            return self
        return None

    def save(self):
        """Updates user in db"""
        if self.uid is None or self.login is None or self.password is None:
            raise ValueError("User model is faked")
        filter = {DB_UID: self.uid, DB_LOGIN: self.login, DB_PASSWORD: self.password}
        query = {'$set': {DB_WORKPLACE: self.workplace_uid}}
        mongo.db.user.update(filter, query)

    def get_id(self):
        return self.uid

    def get_hosts(self, max_count=10):
        if not isinstance(self.uid, ObjectId):
            raise ValueError("Wrong user uid")
        scores_collection = mongo.db.score.find({DB_USER_UID: self.uid}, projection={DB_UID: False, DB_USER_UID: False})
        scores_collection = {s[DB_HOST_UID]: s[DB_SCORE] for s in scores_collection}
        host_collection = mongo.db.host.find({DB_UID: {'$in': scores_collection.keys()}})
        host_collection = {h.pop(DB_UID): h for h in host_collection}
        # if there are not enough host to show them beautifully - add random hosts
        l = len(host_collection)
        if l < max_count:
            addtitional_collection = mongo.db.host.find({DB_UID: {'$nin': scores_collection.keys()}}).limit(max_count-l)
            host_collection.update({h.pop(DB_UID): h for h in addtitional_collection})
        # score is a dict in db, there is a value for every type of lp
        for uid in host_collection:
            host_collection[uid].update({
                'score': scores_collection[uid].get(str(int(host_collection[uid][LOYALITY_TYPE]))) if uid in scores_collection else 0
            })
        return host_collection

    def get_list(self, offset, max_count=10, query=None):
        if not isinstance(self.uid, ObjectId):
            raise ValueError("Wrong user uid")
        scores_collection = mongo.db.score.find({DB_USER_UID: self.uid}, projection={DB_UID: False, DB_USER_UID: False})
        scores_collection = {s[DB_HOST_UID]: s[DB_SCORE] for s in scores_collection}
        scores_len = len(scores_collection)
        host_collection = {}
        if query is not None:
            host_collection = mongo.db.host.find({'$text': {'$search': unicode(query)}}).skip(offset).limit(max_count)
            host_collection = {h.pop(DB_UID): h for h in host_collection}
        else:
            if (scores_len > offset):
                host_collection = mongo.db.host.find({DB_UID: {'$in': scores_collection.keys()}}).skip(offset).limit(max_count)
                host_collection = {h.pop(DB_UID): h for h in host_collection}
            # if there are not enough host to show them beautifully - add random hosts
            l = len(host_collection)
            addtitional_offset = offset - l if offset >= l else 0
            addtitional_limit = max_count if offset >= l else max_count - l
            addtitional_collection = mongo.db.host.find({DB_UID: {'$nin': scores_collection.keys()}}).skip(addtitional_offset).limit(addtitional_limit)
            host_collection.update({h.pop(DB_UID): h for h in addtitional_collection})
        # score is a dict in db, there is a value for every type of lp
        for uid in host_collection:
            host_collection[uid].update({
                'score': scores_collection[uid].get(str(int(host_collection[uid][LOYALITY_TYPE]))) if uid in scores_collection else 0
            })
        return host_collection

    def get_list_map(self):
        if not isinstance(self.uid, ObjectId):
            raise ValueError("Wrong user uid")
        scores_collection = mongo.db.score.find({DB_USER_UID: self.uid}, projection={DB_UID: False, DB_USER_UID: False})
        scores_collection = {s[DB_HOST_UID]: s[DB_SCORE] for s in scores_collection}
        host_collection = {}
        addtitional_collection = mongo.db.host.find({})
        host_collection.update({h.pop(DB_UID): h for h in addtitional_collection})
        # score is a dict in db, there is a value for every type of lp
        for uid in host_collection:
            host_collection[uid].update({
                'score': scores_collection[uid].get(str(int(host_collection[uid][LOYALITY_TYPE]))) if uid in scores_collection else 0
            })
        return host_collection

    @staticmethod
    def retire(uids):
        """Deletes workplace_uid"""
        if ObjectId.is_valid(uids):
            uids = [uids]
        mongo.db.user.update({
            DB_UID: {'$in': map(ObjectId, uids)},
        }, {
            '$set': {DB_WORKPLACE: None}
        })

    def get_host_as_owner(self):
        """Soon will be DEPRECATED. Need to change for many hosts"""
        return mongo.db.host.find_one({OWNER_UID: self.uid}) or {}

    def __repr__(self):
        return '<User %s: %s' % (self.uid, self.login)
