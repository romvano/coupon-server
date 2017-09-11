from extentions import mongo

DB_UID = '_id'
UID = 'uid'
OWNER_UID = 'owner_uid'
STAFF_UIDS = 'staff_uid'
TITLE = 'title'
DESCRIPTION = 'description'
ADDRESS = 'address'
TIME_OPEN = 'time_open'
TIME_CLOSE = 'time_close'
LOGO = 'logo'
LOYALITY_TYPE = 'loyality_type'
LOYALITY_PARAM = 'loyality_param'

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
            self.time_open = time_open
            self.time_close = time_close
            self.logo = logo
            self.loyality_type = loyality_type
            self.loyality_param = loyality_param
        elif uid:
            self.uid = uid
            self.fetch()
        else:
            raise ValueError("Either owner & title or uid must be provided")

    @staticmethod
    def create(data):
        if not all({data.get(OWNER_UID, None), data.get(TITLE, None) is None}):
            return None
        # remove unnecessary fields if they would come
        for key in data:
            if key in HOST_FIELDS:
                data.pop(key)
        return mongo.db.host.insert_one(data).inserted_id

    def fetch(self):
        if self.uid is None:
            return None
        h = mongo.db.host.find_one({DB_UID: self.uid})
        if h is None:
            return None
        self.uid = h.get(DB_UID)
        self.owner_uid = h.get(OWNER_UID)
        self.staff_uids = h.get(STAFF_UIDS)
        self.title = h.get(TITLE)
        self.description = h.get(DESCRIPTION)
        self.address = h.get(ADDRESS)
        self.time_open = h.get(TIME_OPEN)
        self.time_close = h.get(TIME_CLOSE)
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