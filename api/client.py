import os

from flask import Blueprint, session, jsonify, send_from_directory
from flask_login import login_required

from api import user
from models import LOYALITY_PARAM, LATITUDE, LONGITUDE, OFFER, CUP_LOYALITY, PERCENT_LOYALITY
from models.host import TITLE, DESCRIPTION, ADDRESS, TIME_OPEN, TIME_CLOSE, LOGO, LOYALITY_TYPE
from models.user import User

UPLOAD_FOLDER = os.path.split(__file__)[0] + "/.." + "/static/img"

client_bp = Blueprint('client', __name__)

clients = list()

@client_bp.route('register/', methods=['POST'])
def register():
    """DEPRECATED"""
    return user.register()

@client_bp.route('login/', methods=['POST'])
def login_client():
    """DEPRECATED"""
    return user.authenticate()

@client_bp.route('list_hosts/', methods=['GET'])
@login_required
def get_hosts():
    client_id = session['user_id']
    client = User(uid=client_id)
    hosts = [
        {
            'host_id': id,
            'title': host.get(TITLE),
            'description': host.get(DESCRIPTION),
            'offer': host.get(OFFER),
            'address': host.get(ADDRESS),
            'latitude': host.get(LATITUDE),
            'longitude': host.get(LONGITUDE),
            'time_open': host.get(TIME_OPEN),
            'time_close': host.get(TIME_CLOSE),
            'profile_image': host.get(LOGO),
            'points': host.get('score'),
            'loyality_type': int(host[LOYALITY_TYPE]),
            'loyality_param': host.get(LOYALITY_PARAM) if host.get(LOYALITY_TYPE) in {CUP_LOYALITY, PERCENT_LOYALITY} else None,
        } for id, host in client.get_hosts().items()]
    return jsonify({'code': 0, 'hosts': hosts})


@client_bp.route('get_info/', methods=['GET'])
@login_required
def get_info():
    """As we don't have names in db yet, login returned as name"""
    client_id = session['user_id']
    user = User(uid=client_id)
    return jsonify({'code': 0, 'name': user.login, 'identificator': user.uid})


@client_bp.route('media/<filename>', methods=['GET'])
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


@client_bp.route('logout/', methods=['POST'])
@login_required
def logout():
    """DEPRECATED"""
    return user.logout()
