# -*- coding: utf-8 -*-
import os

from flask import Blueprint, jsonify, request, send_from_directory
from flask_api.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_409_CONFLICT, HTTP_403_FORBIDDEN
from flask_login import login_required, current_user

from api import user
from api.common import get_request_data
from extentions import LoyalityJSONDecoder
from models.host import Host, OWNER_UID, TITLE, DESCRIPTION, ADDRESS, TIME_OPEN, TIME_CLOSE, LOYALITY_TYPE, \
    LOYALITY_PARAM
from models.score import Score

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
    host = Host(data)
    host_uid = host.save()
    if host_uid is None:
        return jsonify({'message': "Host with this title (and owner) already exists"}), HTTP_409_CONFLICT
    return jsonify({'code': 0, 'host_id': host_uid, 'message': 'OK'})


@host_bp.route('get_client/', methods=['GET'])
@login_required
def get_client_score():
    data = get_request_data(request)
    client_id = data.get('client_id')
    host_id = data.get('host_id')
    if client_id is None or host_id is None:
        return jsonify({'message': 'both client_id and host_id required'}), HTTP_400_BAD_REQUEST
    score = Score(host_id, client_id).score
    if score is None:
        return jsonify({'message': "No host with this id"}), HTTP_404_NOT_FOUND
    if current_user.uid not in Host(uid=host_id).staff_uids:
        return jsonify({'message': "You don't work here"}), HTTP_403_FORBIDDEN
    return jsonify({'code': 0, 'points': score})


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

@host_bp.route('edit_loyality/', methods=['POST'])
@login_required
def update_loyality():
    """Loyality update. Host id, type and param required"""
    data = get_request_data(request, cls=LoyalityJSONDecoder)
    uid = data.get('host_id')
    if not uid:
        return jsonify({'message': "Uid is None"}), HTTP_400_BAD_REQUEST
    loyality_type, loyality_param = data.get(LOYALITY_TYPE), data.get(LOYALITY_PARAM)
    if not Host.check_loyality(loyality_type, loyality_param):
        return jsonify({'message': "Loyality is wrong"}), HTTP_400_BAD_REQUEST
    host = Host(uid=uid)
    if host.uid is None:
        return jsonify({'message': "No host with uid="+uid+" in db"}), HTTP_404_NOT_FOUND
    if current_user.uid != host.owner_uid:
        return jsonify({'message': "You are not this host"}), HTTP_403_FORBIDDEN
    host.change_loyality(loyality_type, loyality_param)
    return jsonify(SUCCESS)


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

@host_bp.route('media/<filename>', methods=['GET'])
def get_file(filename):
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
    if not file:
        return jsonify({'message': "No file"}), HTTP_400_BAD_REQUEST
    file.save(UPLOAD_FOLDER + "/" + filename)
    host.logo = filename
    host.save()
    return jsonify(SUCCESS)
