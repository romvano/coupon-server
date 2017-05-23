import os
import uuid

from flask import Blueprint, session, jsonify, request, redirect, url_for, send_from_directory
from flask_login import login_required, login_user, logout_user, current_user
from werkzeug.contrib.fixers import ProxyFix
from werkzeug.utils import secure_filename

from api.host import shops
from api.queries import SELECT_ALL_HOSTS, CHECK_USER_FROM_LOGIN, INSERT_USER, GET_USER_FROM_CREDENTAIL, INSERT_CLIENT
from extentions import mysql
from models.user import User
from models.shop import Shop

UPLOAD_FOLDER = os.path.split(__file__)[0] + "/.." + "/static/img"

client_bp = Blueprint('client', __name__)

clients = list()

def get_id(user_id):
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT client_id FROM client WHERE user_id = " + str(user_id))
    result = cursor.fetchone()
    client_id= result[0]
    return client_id


@client_bp.route('register/', methods=['POST'])
def register():
    data = dict((k, v) for (k, v) in request.json.items())
    login = data.get('login', None)
    password = data.get('password', None)
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(CHECK_USER_FROM_LOGIN, [login])
    if cursor.rowcount != 0:
        conn.close()
        return jsonify({'code': 1, 'message': 'already registered'})
    cursor.execute(INSERT_USER, [login, password])
    qr = str(uuid.uuid4())
    cursor.execute(INSERT_CLIENT, [login, qr, cursor.lastrowid])
    session['client_id'] = cursor.lastrowid
    conn.commit()
    conn.close()
    return jsonify({'code': 0, 'message': 'you are registered'})


@client_bp.route('login/', methods=['POST'])
def login_client():
    data = dict((k, v) for (k, v) in request.json.items())
    login = data.get('login', None)
    password = data.get('password', None)

    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(GET_USER_FROM_CREDENTAIL, [login, password])
    if cursor.rowcount == 0:
        conn.close()
        return jsonify({'code': 1, 'message': 'Wrong credentials'})
    user_id = cursor.fetchone()[0]
    client_id= get_id(user_id)
    if 'client_id' in session:
        if current_user and session['client_id'] == client_id:
            session.pop('client_id', None)
            logout_user()
            user = User(login, password)
            login_user(user)
            session['client_id'] = client_id
            conn.close()
            return jsonify({'code': 0, 'message': 'You are already logged in'})
        else:
            session.pop('client_id', None)
            logout_user()
            conn.close()
            return jsonify({'code': 1, 'message': 'You are already logged in as another'})
    user = User(login, password)
    login_user(user)
    session['client_id'] = client_id
    conn.close()
    return jsonify({'code': 0, 'message': 'Logged in'})


@client_bp.route('list_hosts/', methods=['GET'])
def get_shops():
    client_id = session['client_id']
    cursor = mysql.get_db().cursor()

    cursor.execute(SELECT_ALL_HOSTS)
    all_hosts = [i[0] for i in cursor.fetchall()]
    cursor.execute("SELECT host_id, points FROM client_host WHERE client_id = " + str(client_id))
    hostPoints = cursor.fetchall()

    hostsList = []
    for i in hostPoints:
        host_id = i[0]
        points = i[1]
        cursor.execute("SELECT title, description, address, time_open, time_close, profile_image FROM host WHERE host_id = " + str(host_id))
        host = cursor.fetchone()
        host += (points, )
        hostsList.append({"title": host[0], "description": host[1], "address": host[2], "time_open": host[3],
                    "time_close": host[4], "profile_image": host[5], "points": host[6]})
        if (host_id in all_hosts):
            all_hosts.remove(host_id)
    for id in all_hosts:
        cursor.execute(
            "SELECT title, description, address, time_open, time_close, profile_image FROM host WHERE host_id = " + str(id))
        host = cursor.fetchone()
        hostsList.append({"title": host[0], "description": host[1], "address": host[2], "time_open": host[3],
                          "time_close": host[4], "profile_image": host[5], "points": 0})
    cursor.close()
    return jsonify({'code': 0, 'hosts': hostsList})


@client_bp.route('media/<filename>', methods=['GET'])
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


