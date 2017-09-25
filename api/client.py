import os

from flask import Blueprint, session, jsonify, request, redirect, url_for, send_from_directory
from flask_login import login_required, login_user, logout_user, current_user
from extentions import mysql

from api import user
from api.queries import SELECT_ALL_HOSTS, SELECT_NAME_IDENTIFICATOR_FROM_CLIENT

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
def get_shops():
    client_id = session['client_id']
    cursor = mysql.get_db().cursor()

    cursor.execute(SELECT_ALL_HOSTS)
    all_hosts = [i[0] for i in cursor.fetchall()]
    cursor.execute("SELECT host_id, amount FROM score WHERE client_id = " + str(client_id))
    hostPoints = cursor.fetchall()

    hostsList = []
    for i in hostPoints:
        host_id = i[0]
        points = i[1]
        cursor.execute(
            "SELECT title, description, address, time_open, time_close, profile_image FROM host WHERE host_id = " + str(
                host_id))
        host = cursor.fetchone()
        host += (points,)
        hostsList.append({"title": host[0], "description": host[1], "address": host[2], "time_open": host[3],
                          "time_close": host[4], "profile_image": host[5], "points": host[6]})
        if (host_id in all_hosts):
            all_hosts.remove(host_id)
    for id in all_hosts:
        cursor.execute(
            "SELECT title, description, address, time_open, time_close, profile_image FROM host WHERE host_id = " + str(
                id))
        host = cursor.fetchone()
        hostsList.append({"title": host[0], "description": host[1], "address": host[2], "time_open": host[3],
                          "time_close": host[4], "profile_image": host[5], "points": 0})
    cursor.close()
    return jsonify({'code': 0, 'hosts': hostsList})


@client_bp.route('get_info/', methods=['GET'])
@login_required
def get_info():
    client_id = session['client_id']
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
