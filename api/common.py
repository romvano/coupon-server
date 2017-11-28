# -*- coding: utf-8 -*-

import json

from flask.globals import session
from flask_login.utils import current_user

from extentions import lm
from models.user import User

@lm.user_loader
def load_user(uid):
    return User(uid=uid)


def get_request_data(request, cls=None):
    if request.method == 'POST':
        if request.json is None:
            data = json.loads(request.data, cls=cls) if request.data else {}
        else:
            data = dict((k, v) for (k, v) in request.json.items())
        return data
    if request.method == 'GET':
        data = dict((k, v) for (k, v) in request.args.items())
        return data

def get_current_host_id():
    """For the cases if host_id not in session but the host is already created"""
    host_uid = session.get('host_id')
    if host_uid is None:
        host_uid = session['host_id'] = current_user.workplace_uid
    return host_uid
