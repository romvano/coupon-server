# -*- coding: utf-8 -*-
import os

import MySQLdb
from flask import Blueprint, session, jsonify, request, send_from_directory
from flask_api.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_304_NOT_MODIFIED, HTTP_409_CONFLICT, \
    HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN
from flask_login import login_required, login_user, logout_user, current_user
from werkzeug.utils import secure_filename

from api import user
from api.common import get_request_data
from api.queries import INSERT_OPERATION_ADD, INSERT_OPERATION_WITHDRAW, SELECT_INFO, EDIT_HOST, \
    UPLOAD_PHOTO, GET_USER_FROM_CREDENTAIL, CHECK_USER_FROM_LOGIN, INSERT_USER, INSERT_HOST, UPDATE_NEW_HOST, \
    CHECK_HOST_CLIENT, INSERT_CLIENT_HOST
from extentions import mysql
from models.host import Host, OWNER_UID, STAFF_UIDS, TITLE, DESCRIPTION, ADDRESS, TIME_OPEN, TIME_CLOSE

from flask import current_app

SUCCESS = {'code': 0, 'message': 'OK'}
HOST_CREATION_FAILED = {'message': 'Unabled to create host. Title required'}
HOST_NOT_FOUND = {'message': 'Host not found'}

UPLOAD_FOLDER = os.path.split(__file__)[0] + "/.." + "/static/img"

host_bp = Blueprint('host_bp', __name__)

@host_bp.route('register/', methods=['POST'])
def register_host():
    """DEPRECATED"""
    return user.authenticate()


@host_bp.route('login/', methods=['POST'])
def login():
    """DEPRECATED"""
    return user.authenticate()

@host_bp.route('logout/', methods=['POST'])
@login_required
def logout():
    """DEPRECATED"""
    return user.logout()

@host_bp.route('create/', methods=['POST'])
@login_required
def create_host():
    """Required: title"""
    data = get_request_data(request)
    if not data.get(TITLE):
        return jsonify(HOST_CREATION_FAILED), HTTP_400_BAD_REQUEST
    data[OWNER_UID] = current_user.uid
    data[STAFF_UIDS] = {current_user.uid,}.union(data.get(STAFF_UIDS, set()))
    host = Host.create(data)
    if host is None:
        return jsonify(HOST_CREATION_FAILED), HTTP_409_CONFLICT
    return jsonify(SUCCESS)


@host_bp.route('get_client/<identificator>/', methods=['GET'])
def get_client(identificator):
    host_id = str(session['host_id'])
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT amount FROM score WHERE host_id = " + host_id + " AND client_id = \
                        (SELECT client_id FROM client WHERE identificator = '" + identificator + "')")
    points = cursor.fetchone()[0]
    print points
    response = {'code': 0, 'points': points}
    conn.close()
    return jsonify(response)


# @host_bp.route('statistic/', methods=['GET'])
# def get_statistic():
#     host_id = str(session['host_id'])
#     conn = mysql.connect()
#     cursor = conn.cursor()
#     cursor.execute(SELECT_STATISTIC, [host_id])
#     operations = cursor.fetchall()
#     response = []
#     for i in operations:
#         date = i[0]
#         avg_bill = i[1]
#         income = i[2]
#         outcome = i[3]
#         response.append({"date": date, "avg_bill": avg_bill, "income": income, "outcome": outcome})
#     conn.close()
#     return jsonify({"code": 0, "response": response})


@host_bp.route('info/', methods=['GET'])
@login_required
def get_info():
    host_id = get_request_data(request).get('host_id')
    if not host_id:
        return jsonify({'message': "No host id provided"}), HTTP_400_BAD_REQUEST
    host = Host(uid=host_id)
    # 404 if there is a host with no title in db. No unnamed hosts allowed.
    response = host.to_dict()
    if response is None:
        return jsonify({'message': "No such host in db"}), HTTP_404_NOT_FOUND
    return jsonify(response)


@host_bp.route('edit_host/', methods=['POST'])
@login_required
def update_host():
    """All fields updated at a time"""
    data = get_request_data(request)
    uid = data.get('host_id')
    if not uid:
        return jsonify({'message': "Uid is None"}), HTTP_400_BAD_REQUEST
    if not data.get(TITLE):
        return jsonify({'message': "Title required"}), HTTP_400_BAD_REQUEST
    host = Host(uid=uid)
    if host.uid is None:
        return jsonify({'message': "No host with uid="+uid+" in db"}), HTTP_404_NOT_FOUND
    if current_user.uid != host.owner_uid:
        return jsonify({'message': "You are not this host"}), HTTP_403_FORBIDDEN
    host.title = data[TITLE]
    host.description = data.get(DESCRIPTION)
    host.address = data.get(ADDRESS)
    host.time_open = Host.parse_time(data.get(TIME_OPEN))
    host.time_close = Host.parse_time(data.get(TIME_CLOSE))
    result_uid = host.save()
    if result_uid is None:
        return jsonify({'message': "Update failed"}), HTTP_409_CONFLICT
    return jsonify(host.to_dict())


@host_bp.route('delete/', methods=['POST'])
@login_required
def delete_host():
    data = get_request_data(request)
    uid = data.get('host_id')
    if not uid:
        return jsonify({'message': "Uid is None"}), HTTP_400_BAD_REQUEST
    host = Host(uid=uid)
    if host.uid is None:
        return jsonify({'message': "No host with uid="+uid+" in db"}), HTTP_404_NOT_FOUND
    if current_user.uid != host.owner_uid:
        return jsonify({'message': "You are not this host"}), HTTP_403_FORBIDDEN
    host.delete()
    return jsonify({'code': 0})



@host_bp.route('update_points/', methods=['POST'])
@login_required
def update_points():
    data = dict((k, v) for (k, v) in request.json.items())

    host_id = str(session['host_id'])
    bill = data.get('bill', None)
    is_add = data.get('is_add', None)
    client_identificator = data.get('client_identificator', None)

    conn = mysql.connect()
    cursor = conn.cursor()

    cursor.execute(CHECK_HOST_CLIENT,[host_id, client_identificator])
    has_been = cursor.fetchone()
    if has_been == None:
        cursor.execute(INSERT_CLIENT_HOST, [host_id,client_identificator])
        conn.commit()

    # TO_DO: add_percent make dynamic
    if is_add:
        cursor.execute("SELECT 10 FROM host WHERE host_id = " + host_id)   # 10 until I create loyalityscheme
        add_percent = float(cursor.fetchone()[0]) / 100
        add_points = str(int(bill * add_percent))
        cursor.execute("UPDATE score SET amount = amount + " + add_points + " WHERE host_id = " + host_id + " AND client_id = \
                                (SELECT client_id FROM client WHERE identificator = '" + client_identificator + "')")
        cursor.execute(INSERT_OPERATION_ADD, [host_id, add_points, 0, client_identificator])

        response = {'code': 0, 'message': 'Бонусы были успешно зачислены'}
    else:
        cursor.execute("SELECT amount FROM score WHERE host_id = " + host_id + " AND client_id = \
                                (SELECT client_id FROM client WHERE identificator = '" + client_identificator + "')")
        points = int(cursor.fetchone()[0])
        if points >= bill:
            points = str(points - bill)
            cursor.execute(
                "UPDATE score SET amount = " + points + " WHERE host_id = " + host_id + " AND client_id = \
                                            (SELECT client_id FROM client WHERE identificator = '" + client_identificator + "')")
            cursor.execute(INSERT_OPERATION_WITHDRAW, [host_id, bill, 1, client_identificator])

            response = {'code': 0, 'message': 'Бонусы были успешно списаны'}
        else:
            response = {'code': 0, 'message': 'Извините, но бонусов не хватает'}
    conn.commit()
    conn.close()
    return jsonify(response)


@host_bp.route('testsession/', methods=['GET'])
def test_session():
    current_app.logger.info('grolsh')
    return jsonify({'code': 0, 'message': 'wonderful!'})


@host_bp.route('media/<filename>', methods=['GET'])
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


@host_bp.route('upload/', methods=['POST'])
@login_required
def upload():
    uid = get_request_data(request).get('host_id')
    if not uid:
        return jsonify({'message': "Host id must be provided"}), HTTP_400_BAD_REQUEST
    host = Host(uid=uid)
    if host.uid is None:
        return jsonify({'message': "No host with uid="+uid+" in db"}), HTTP_404_NOT_FOUND
    if current_user.uid != host.owner_uid:
        return jsonify({'message': "You are not this host"}), HTTP_403_FORBIDDEN
    # name the new file based on host uid
    current_picture_name = host.logo
    if current_picture_name is None:
        filename = host.uid + '_0'
    else:
        number = current_picture_name.split('_')[-1]
        if not number.isdecimal():
            filename = host.uid + '_0'
        else:
            number = int(number) + 1
            filename = host.uid + '_' + str(number)
    file = request.files.get("picture")
    file.save(UPLOAD_FOLDER + "/" + filename)
    host.logo = filename
    host.save()
    return jsonify(SUCCESS)
