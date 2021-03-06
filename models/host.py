# -*- coding: utf-8 -*-
import datetime

from bson.errors import InvalidId
from bson.objectid import ObjectId
from pymongo.errors import DuplicateKeyError

from extentions import mongo

from models.__init__ import *


class Host():
    def __init__(self, data={}, uid=None):
        """Init Host. Logo and staff uids, loyality params should be set additionally"""
        if all({OWNER_UID in data and data[OWNER_UID],
                TITLE in data and data[TITLE]}):
            self.uid = None
            self.owner_uid = ObjectId(data[OWNER_UID])
            self.staff_uids = {self.owner_uid,}
            self.title = data.get(TITLE)
            self.description = data.get(DESCRIPTION)
            self.address = data.get(ADDRESS)
            self.latitude = data.get(LATITUDE)
            self.longitude = data.get(LONGITUDE)
            self.time_open = Host.parse_time(data.get(TIME_OPEN))
            self.time_close = Host.parse_time(data.get(TIME_CLOSE))
            self.logo = None
            self.loyality_type = PERCENT_LOYALITY
            self.loyality_param = 10
            self.loyality_burn_param = NO_BURN # 0 - all bonuses, 1 - partially, None - no burn
            self.loyality_time_param = 30 # number of days until bonus burns
            self.offer = self.create_offer()
        elif uid:
            try:
                self.uid = ObjectId(uid)
                self.fetch()
            except InvalidId:
                self.uid = None
                self.title = None
        else:
            raise ValueError("Either owner & title or uid must be provided")

    def create_offer(self):
        def parse_days(n):
            if n % 10 == 1 and n != 11:
                return str(n) + " день"
            if n % 10 in (2, 3, 4) and n not in (12, 13):
                return str(n) + " дня"
            return str(n) + " дней"

        burn = ""
        if self.loyality_burn_param == BURN_ALL:
            burn = " Ваш счет обнулится через " + parse_days(self.loyality_time_param) + " после последней покупки"
        elif self.loyality_burn_param == BURN_PARTIALLY:
            burn = " Бонусы от покупки сгорают через " + parse_days(self.loyality_time_param)
        if self.loyality_type == CUP_LOYALITY:
            self.offer = "Каждая " + str(int(self.loyality_param)) + "-я покупка - в подарок!" + burn
        elif self.loyality_type == PERCENT_LOYALITY:
            self.offer = str(int(self.loyality_param)) + "% от покупок возвращается бонусами!" + burn
        elif self.loyality_type == DISCOUNT_LOYALITY:
            self.offer = "А эта программа лояльности пока не работает =)" + burn
        return self.offer

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
        return None

    @staticmethod
    def create(data):
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
        data[OFFER] = self.offer or self.create_offer()
        if self.address is not None:
            data[ADDRESS] = self.address
        if self.latitude is not None and self.longitude is not None:
            data[LATITUDE], data[LONGITUDE] = self.latitude, self.longitude
        if self.time_open is not None:
            data[TIME_OPEN] = Host.parse_time(self.time_open).isoformat()[:5]
        if self.time_close is not None:
            data[TIME_CLOSE] = Host.parse_time(self.time_close).isoformat()[:5]
        if self.logo is not None:
            data[LOGO] = self.logo
        if self.loyality_type is not None:
            data[LOYALITY_TYPE] = self.loyality_type
        if self.loyality_param is not None:
            data[LOYALITY_PARAM] = self.loyality_param
        data[LOYALITY_TIME_PARAM] = self.loyality_time_param or None
        data[LOYALITY_BURN_PARAM] = self.loyality_burn_param or None
        # update or create new?
        try:
            if self.uid:
                upsert = mongo.db.host.replace_one({DB_UID: self.uid}, data, upsert=True)
                if upsert.upserted_id:
                    return upsert.upserted_id
                if upsert.modified_count > 0:
                    return self.uid
                return None
            self.uid = mongo.db.host.insert_one(data).inserted_id
            return self.uid
        except DuplicateKeyError:
            return None

    def fetch(self):
        if self.uid is None:
            raise ValueError("self.uid is None")
        h = mongo.db.host.find_one({DB_UID: self.uid})
        if h is None:
            h = {}
        self.uid = h.get(DB_UID)
        self.owner_uid = h.get(OWNER_UID)
        self.staff_uids = h.get(STAFF_UIDS) and set(h.get(STAFF_UIDS))
        self.title = h.get(TITLE)
        self.description = h.get(DESCRIPTION)
        self.address = h.get(ADDRESS)
        self.latitude = h.get(LATITUDE)
        self.longitude = h.get(LONGITUDE)
        if h.get(TIME_OPEN):
            self.time_open = datetime.datetime.strptime(h[TIME_OPEN], TIME_FORMAT).time()
        else:
            self.time_open = None
        if h.get(TIME_CLOSE):
            self.time_close = datetime.datetime.strptime(h[TIME_CLOSE], TIME_FORMAT).time()
        else:
            self.time_close = None
        self.logo = h.get(LOGO)
        self.loyality_type = h.get(LOYALITY_TYPE) and int(h[LOYALITY_TYPE])
        self.loyality_param = h.get(LOYALITY_PARAM)
        self.loyality_time_param = h.get(LOYALITY_TIME_PARAM) and int(h[LOYALITY_TIME_PARAM])
        self.loyality_burn_param = h.get(LOYALITY_BURN_PARAM) and int(h[LOYALITY_BURN_PARAM])
        self.offer = h.get(OFFER) or self.create_offer()
        # compability
        print 'ltp: ', str(self.loyality_time_param)
        if self.loyality_time_param is None:
            self.loyality_time_param = 30
            self.save()
        return self

    def delete(self):
        if self.uid is None:
            raise ValueError("self.uid is None")
        mongo.db.host.remove({DB_UID: self.uid})

    @staticmethod
    def check_loyality(lt, lp, ltp, lbp):
        def check_burn(ltp, lbp):
            return lbp in LOYALITY_BURNS and ltp > 0

        def check_type_and_param(lt, lp):
            if lt not in LOYALITY_TYPES:
                return False
            if lt in (CUP_LOYALITY, PERCENT_LOYALITY):
                return lp > 0
            if lt == DISCOUNT_LOYALITY:
                return isinstance(lp, dict) and all(i > 0 for i in (lp.keys() + lp.values()))

        return check_type_and_param(lt, lp) and check_burn(ltp, lbp)

    def change_loyality(self, loyality_type, loyality_param, loyality_time=30, loyality_burn=NO_BURN, offer=None):
        """Should be called after fetch"""
        if not self.check_loyality(loyality_type, loyality_param, loyality_time, loyality_burn):
            raise ValueError("Wrong loyality")
        self.loyality_type = loyality_type
        self.loyality_param = loyality_param
        self.loyality_time_param = loyality_time
        self.loyality_burn_param = loyality_burn
        self.offer = offer or self.create_offer()
        self.save()

    def get_discount(self, amount):
        """Only for discount loyality type"""
        if self.loyality_type != DISCOUNT_LOYALITY:
            raise ValueError("Wrong loyality type")
        thresholds = self.loyality_param.keys()
        thresholds.sort(cmp=lambda x, y: y - x)
        for i in thresholds:
            if i <= amount:
                return float(self.loyality_param[i]) / 100
        return 0

    def retire(self, worker_uid):
        """if worker_uid == 'all' then it's finance crisis (retire everybody)"""
        if worker_uid != 'all' and ObjectId(worker_uid) not in self.staff_uids \
                or ObjectId(worker_uid) == self.owner_uid:
            raise ValueError("worker_uid should be ObjectId and in staff_uids")
        user_uids_to_retire = self.staff_uids.copy()
        user_uids_to_retire.remove(self.owner_uid)
        if worker_uid == 'all':
            self.staff_uids = {self.owner_uid,}
        else:
            self.staff_uids.remove(ObjectId(worker_uid))
        self.save()
        return user_uids_to_retire

    def get_staff(self):
        filter = {DB_UID: {'$in': list(self.staff_uids)}}
        return list(mongo.db.user.find(filter,
                                       projection={DB_UID: True, DB_LOGIN: True}))

    def hire(self, uid):
        self.staff_uids.add(ObjectId(uid))
        self.save()

    def get_id(self):
        return self.uid

    def to_dict(self):
        if not self.title or not self.owner_uid:
            return None
        response = {
            "title": self.title,
            "description": self.description,
            "offer": self.create_offer(),
            "address": self.address,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "time_open": self.time_open.isoformat()[:5] if self.time_open else None,
            "time_close": self.time_close.isoformat()[:5] if self.time_close else None,
            "profile_image": self.logo,
            "loyality_type": self.loyality_type,
            "loyality_param": self.loyality_param,
            "loyality_time_param": self.loyality_time_param,
            "loyality_burn_param": self.loyality_burn_param,
        }
        return response

    def __repr__(self):
        return '<Host %s: %s by %s' % (str(self.uid), str(self.title), str(self.owner_uid))
