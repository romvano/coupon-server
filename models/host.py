# -*- coding: utf-8 -*-
import datetime

from bson.errors import InvalidId
from bson.objectid import ObjectId
from pymongo.errors import DuplicateKeyError

from extentions import mongo

DB_UID = '_id'
UID = 'uid'
OWNER_UID = 'owner_uid'
STAFF_UIDS = 'staff_uids'
TITLE ='title'
DESCRIPTION = 'description'
ADDRESS = 'address'
TIME_OPEN = 'time_open'
TIME_CLOSE = 'time_close'
LOGO = 'logo'
LOYALITY_TYPE = 'loyality_type'
LOYALITY_PARAM = 'loyality_param'

TIME_FORMAT = '%H:%M'

HOST_FIELDS = {OWNER_UID, STAFF_UIDS, TITLE, DESCRIPTION, ADDRESS,
               TIME_OPEN, TIME_CLOSE, LOGO, LOYALITY_TYPE, LOYALITY_PARAM}


class Host():
    def __init__(self, data=dict(), uid=None):
        """Init Host. Logo and staff uids, loyality params should be set additionally"""
        if all({OWNER_UID in data and data[OWNER_UID],
                TITLE in data and data[TITLE]}):
            self.uid = data.get(UID)
            self.owner_uid = data.get(OWNER_UID)
            self.staff_uids = {self.owner_uid,}
            self.title = data.get(TITLE)
            self.description = data.get(DESCRIPTION)
            self.address = data.get(ADDRESS)
            self.time_open = Host.parse_time(data.get(TIME_OPEN))
            self.time_close = Host.parse_time(data.get(TIME_CLOSE))
            self.logo = None
            self.loyality_type = None
            self.loyality_param = None
        elif uid:
            try:
                ObjectId(uid)
            except InvalidId:
                self.uid = None
                self.title = None
            else:
                self.uid = uid
                self.fetch()
        else:
            raise ValueError("Either owner & title or uid must be provided")

    @staticmethod
    def parse_time(t):
        """For compability with strange time format"""
        if isinstance(t, str) or isinstance(t, unicode):
            if t.isdecimal():
                t = int(t)
            else:
                try:
                    return datetime.datetime.strptime(t[:5], TIME_FORMAT).time()
                except ValueError:
                    return datetime.time()
        if isinstance(t, int):
            return datetime.time(t / 24, t % 24)
        if isinstance(t, datetime.time):
            return t
        return datetime.time()

    @staticmethod
    def create(data):
        # setting staff allowed only in update host
        host = Host(data)
        uid = host.save()
        return host if uid else None

    def save(self):
        if self.owner_uid is None or self.title is None:
            return None
        data = {} # dict to pass to db
        data[OWNER_UID] = self.owner_uid
        data[STAFF_UIDS] = list(self.staff_uids)
        data[TITLE] = self.title
        if self.description is not None:
            data[DESCRIPTION] = self.description
        if self.address is not None:
            data[ADDRESS] = self.address
        if self.time_open:
            data[TIME_OPEN] = Host.parse_time(self.time_open).isoformat()[:5] if self.time_open else None
        if self.time_close:
            data[TIME_CLOSE] = Host.parse_time(self.time_close).isoformat()[:5] if self.time_close else None
        if self.logo:
            data[LOGO] = self.logo
        if self.loyality_type:
            data[LOYALITY_TYPE] = self.loyality_type
        if self.loyality_param:
            data[LOYALITY_PARAM] = self.loyality_param
        # update or create new?
        try:
            if self.uid:
                upsert = mongo.db.host.replace_one({DB_UID: self.uid}, data, upsert=True)
                if upsert.upserted_id:
                    return upsert.upserted_id
                if upsert.modified_count > 0:
                    return self.uid
                return None
            return mongo.db.host.insert_one(data).inserted_id
        except DuplicateKeyError:
            return None

    def fetch(self):
        if self.uid is None:
            raise ValueError("self.uid is None")
        h = mongo.db.host.find_one({DB_UID: ObjectId(self.uid)})
        if h is None:
            h = {}
        self.uid = h.get(DB_UID)
        self.owner_uid = h.get(OWNER_UID)
        self.staff_uids = set(h.get(STAFF_UIDS)) if h.get(STAFF_UIDS) else None
        self.title = h.get(TITLE)
        self.description = h.get(DESCRIPTION)
        self.address = h.get(ADDRESS)
        if TIME_OPEN in h:
            self.time_open = datetime.datetime.strptime(h.get(TIME_OPEN), TIME_FORMAT).time()
        else:
            self.time_open = None
        if TIME_CLOSE in h:
            self.time_close = datetime.datetime.strptime(h.get(TIME_CLOSE), TIME_FORMAT).time()
        else:
            self.time_close = None
        self.logo = h.get(LOGO)
        self.loyality_type = h.get(LOYALITY_TYPE)
        self.loyality_param = h.get(LOYALITY_PARAM)
        return self

    def delete(self):
        if self.uid is None:
            raise ValueError("self.uid is None")
        mongo.db.host.remove({DB_UID: ObjectId(self.uid)})

    def change_loyality(self, loyality_type, loyality_param):
        # TODO
        pass

    def get_id(self):
        return self.uid

    def to_dict(self):
        if not self.title or not self.owner_uid:
            return None
        response = {
            "title": self.title,
            "description": self.description,
            "address": self.address,
            "time_open": self.time_open.isoformat()[:5] if self.time_open else None,
            "time_close": self.time_close.isoformat()[:5] if self.time_close else None,
            "profile_image": self.logo,
            "loyality_type": self.loyality_type,
            "loyality_param": self.loyality_param,
        }
        return response

    def __repr__(self):
        return '<Host %s: %s by %s' % (str(self.uid), str(self.title), str(self.owner_uid))

 #    def delete():
 #        pass