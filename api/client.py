import os

from flask import Blueprint, session, jsonify, request, redirect, url_for, send_from_directory
from flask_login import login_required, login_user, logout_user, current_user
from werkzeug.contrib.fixers import ProxyFix
from werkzeug.utils import secure_filename

from api.host import shops
from extentions import mysql
from models.user import User
from models.shop import Shop

UPLOAD_FOLDER = os.path.split(__file__)[0] + "/.." + "/static/img"

client_bp = Blueprint('client', __name__)

clients = list()


@client_bp.route('register/', methods=['POST'])
def register():
    data = dict((k, v) for (k, v) in request.json.items())
    login = data.get('login', None)
    password = data.get('password', None)
    if login != None and password != None:
        for user in clients:
            if user.login == login:
                return jsonify({'code': 1, 'message': 'already registered'})
        clients.append(User(login, password))
        return jsonify({'code': 0, 'message': 'you are registered'})
    return jsonify({'code': 1, 'message': 'wrong login/password'})


@client_bp.route('login/', methods=['POST'])
def login_client():
    data = dict((k, v) for (k, v) in request.json.items())
    login = data.get('login', None)
    password = data.get('password', None)
    user = User(login, password)
    valid = False
    for user in clients:
        if user.login == login and user.password == password:
            valid = True
    if valid:
        if 'username' in session:
            if current_user and session['username'] == login:
                return jsonify({'code': 0, 'message': 'already logged in'})
            else:
                return jsonify({'code': 1, 'message': 'already logged in as another'})
        user = User(login, password)
        login_user(user)
        session['username'] = login
        return jsonify({'code': 0, 'message': 'logged in'})
    return jsonify({'code': 1, 'message': 'wrong credentials'})


@client_bp.route('list_hosts/', methods=['POST'])
def get_shops():
    data = dict((k, v) for (k, v) in request.json.items())
    client_id = data.get("client_id", None)

    cursor = mysql.get_db().cursor()
    cursor.execute("SELECT host_id, points FROM client_host WHERE client_id = " + str(client_id))
    hostPoints = cursor.fetchall()
    hostsList = []
    for i in hostPoints:
        host_id = i[0]
        points = i[1]
        cursor.execute("SELECT title, description, address, time_open, time_close FROM host WHERE host_id = " + str(host_id))
        host = cursor.fetchone()
        host += (points, )
        hostsList.append({"title": host[0], "description": host[1], "address": host[2], "time_open": host[3],
                    "time_close": host[4], "profile_image": "jhdun.jpg", "points": host[5]})
        
    print hostsList
    # shopList = list()
    # for shop in shops:
    #     shopDict = {"title": shop.title, "description": shop.description, "logo": shop.logo}
    #     shopList.append(shopDict)
    cursor.close()
    return jsonify({'code': 0, 'hosts': hostsList})


@client_bp.route('media/<filename>', methods=['GET'])
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


