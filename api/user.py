# -*- coding: utf-8 -*-

from flask.blueprints import Blueprint
from flask.globals import session, request
from flask.json import jsonify
from flask_api.status import HTTP_409_CONFLICT, HTTP_400_BAD_REQUEST
from flask_login.utils import login_user, current_user, logout_user, login_required

from api.common import get_request_data
from models.host import DB_UID
from models.user import User

WRONG_CREDS = {'code': 1, 'message': 'Wrong creds'}
SUCCESS = {'code': 0, 'message': 'OK'}
ALREADY_AUTHED = {'code': 1, 'message': 'OK'}
USER_EXISTS = {'message': 'User exists'}

user_bp = Blueprint('user', __name__)

def _get_creds(request):
    data = get_request_data(request)
    return data.get('login', None), data.get('password', None)

@user_bp.route('login/', methods=['POST'])
def authenticate():
    """Returns user_id, host_id if exists"""
    login, pwd = _get_creds(request)
    if login is None or pwd is None:
        return jsonify({'message': "login and password should be provided"}), HTTP_400_BAD_REQUEST
    if 'user_id' in session:
        logout()
    user = User(login=str(login), pwd=str(pwd))
    result = user.fetch()
    if result == None:
        return jsonify(WRONG_CREDS)
    login_user(user, remember=True)
    host_uid = user.get_host_as_owner().get(DB_UID)
    session['host_id'] = user.workplace_uid
    return jsonify({'code': 0, 'user_id': user.uid, 'host_id': host_uid})

@user_bp.route('register/', methods=['POST'])
def register():
    login, pwd = _get_creds(request)
    if login is None or pwd is None:
        return jsonify({'message': "login and password should be provided"}), HTTP_400_BAD_REQUEST
    if 'user_id' in session:
        return jsonify(ALREADY_AUTHED)
    uid = User.create(login=str(login), pwd=str(pwd))
    if uid is None:
        return jsonify(USER_EXISTS), HTTP_409_CONFLICT
    user = User(uid=uid)
    if user is None:
        return jsonify(WRONG_CREDS)
    return jsonify(SUCCESS)

@user_bp.route('logout/', methods=['POST'])
def logout():
    session.pop('host_id', None)
    logout_user()
    return jsonify(SUCCESS)

@user_bp.route('get_workplace/', methods=['GET'])
@login_required
def get_workplace():
    user_id = session.get('user_id')
    user = User(user_id)
    if user.workplace_uid is not None:
        session['host_id'] = user.workplace_uid
    else:
        session.pop('host_id', None)
    return jsonify({'code': 0, 'host_id': user.workplace_uid})
