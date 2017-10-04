import os

from flask import Blueprint, session, jsonify, request, redirect, url_for, send_from_directory
from flask_login import login_required, login_user, logout_user, current_user
from extentions import mysql

from api import user
from api.queries import SELECT_ALL_HOSTS, SELECT_NAME_IDENTIFICATOR_FROM_CLIENT
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
            'address': host.get(ADDRESS),
            'time_open': host.get(TIME_OPEN),
            'time_close': host.get(TIME_CLOSE),
            'profile_image': host.get(LOGO),
            'points': host.get('score'),
            'loyality_type': host.get(LOYALITY_TYPE),
        } for id, host in client.get_hosts().items()]
    return jsonify({'code': 0, 'hosts': hosts})


@client_bp.route('get_info/', methods=['GET'])
@login_required
def get_info():
    client_id = session['user_id']
    conn = mysql.connect()
    cursor = conn.cursor()

    cursor.execute(SELECT_NAME_IDENTIFICATOR_FROM_CLIENT, [client_id])
    result = cursor.fetchone()
    name = result[0]
    identificator = result[1]

    return jsonify({'code': 0, 'name': name, 'identificator': identificator})



@client_bp.route('media/<filename>', methods=['GET'])
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


@client_bp.route('logout/', methods=['POST'])
@login_required
def logout():
    """DEPRECATED"""
    return user.logout()
