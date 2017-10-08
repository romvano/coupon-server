# Host constants
DB_UID = '_id'
UID = 'uid'
OWNER_UID = 'owner_uid'
STAFF_UIDS = 'staff_uids'
TITLE = 'title'
DESCRIPTION = 'description'
ADDRESS = 'address'
TIME_OPEN = 'time_open'
TIME_CLOSE = 'time_close'
LOGO = 'logo'
LOYALITY_TYPE = 'loyality_type'
LOYALITY_PARAM = 'loyality_param'

CUP_LOYALITY = 0
PERCENT_LOYALITY = 1
DISCOUNT_LOYALITY = 2
LOYALITY_TYPES = {CUP_LOYALITY, PERCENT_LOYALITY, DISCOUNT_LOYALITY}

TIME_FORMAT = '%H:%M'

HOST_FIELDS = {OWNER_UID, STAFF_UIDS, TITLE, DESCRIPTION, ADDRESS,
               TIME_OPEN, TIME_CLOSE, LOGO, LOYALITY_TYPE, LOYALITY_PARAM}

# User constants
DB_LOGIN = 'login'
DB_PASSWORD = 'password'
DB_WORKPLACE = 'workplace'

# Score constants
DB_HOST_UID = 'host_uid'
DB_USER_UID = 'user_uid'
DB_SCORE = 'score'
