# -*- coding: utf-8 -*-
import datetime

from extentions import mongo

DB_UID = '_id'
UID = 'uid'
OWNER_UID = 'owner_uid'
STAFF_UIDS = 'staff_uid'
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
    def __init__(self, uid=None, owner_uid=None, staff_uids=set(), title=None, description=None, address=None,
                 time_open=None, time_close=None, logo=None, loyality_type=None, loyality_param=None):
        if all({owner_uid, title}):
            self.uid = uid
            self.owner_uid = owner_uid
            self.staff_uids = set(staff_uids)
            self.title = title
            self.description = description
            self.address = address
            self.time_open = Host.parse_time(time_open)
            self.time_close = Host.parse_time(time_close)
            self.logo = logo
            self.loyality_type = loyality_type
            self.loyality_param = loyality_param
        elif uid:
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
        if not (data.get(OWNER_UID, None) and data.get(TITLE, None)):
            return None
        # remove unnecessary fields if they would come
        for key in data.keys():
            if key not in HOST_FIELDS:
                data.pop(key)
        data[STAFF_UIDS] = list(data[STAFF_UIDS])
        if TIME_OPEN in data:
            data[TIME_OPEN] = Host.parse_time(data[TIME_OPEN]).isoformat()[:5]
        if TIME_CLOSE in data:
            data[TIME_CLOSE] = Host.parse_time(data[TIME_CLOSE]).isoformat()[:5]
        return mongo.db.host.insert_one(data).inserted_id

    def fetch(self):
        if self.uid is None:
            return None
        h = mongo.db.host.find_one({DB_UID: self.uid})
        if h is None:
            return None
        self.uid = h.get(DB_UID)
        self.owner_uid = h.get(OWNER_UID)
        self.staff_uids = set(h.get(STAFF_UIDS))
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

    def get_id(self):
        return self.uid

    def __repr__(self):
        return '<Host %s: %s by %s' % (self.uid, self.title, self.owner_uid)

 #    def delete():
 #        pass