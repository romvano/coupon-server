# -*- coding: utf-8 -*-
from flask.blueprints import Blueprint
from flask.globals import g, session
from flask.json import jsonify
from flask_api.status import HTTP_409_CONFLICT
from flask_login.utils import login_user, current_user, logout_user

from models.user import User

WRONG_CREDS = {'code': 1, 'message': 'Wrong creds'}
SUCCESS = {'code': 0, 'message': 'OK'}
ALREADY_AUTHED = {'code': 1, 'message': 'OK'}
USER_EXISTS = {'message': 'User exists'}

user_bp = Blueprint('user', __name__)

@user_bp.route('register/', methods=['POST'])
def authenticate(login, pwd):
    if 'login' in session:
        logout()
    user = User(login=login, pwd=pwd)
    result = user.fetch()
    if result == None:
        return jsonify(WRONG_CREDS)
    login_user(user, remember=True)
    g.user = current_user
    session['login'] = g.user.login
    return jsonify(SUCCESS)

@user_bp.route('login/', methods=['POST'])
def register(login, pwd):
    if 'login' in session:
        return jsonify(ALREADY_AUTHED)
    uid = User.create(login=login, pwd=pwd)
    if uid is None:
        return jsonify(USER_EXISTS), HTTP_409_CONFLICT
    user = User(uid=uid)
    if user is None:
        return jsonify(WRONG_CREDS)
    return jsonify(SUCCESS)

@user_bp.route('logout/', methods=['POST'])
def logout():
    session.pop('client_id', None)
    logout_user()
    return jsonify(SUCCESS)
