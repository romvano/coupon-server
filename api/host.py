# -*- coding: utf-8 -*-
import os

from bson.objectid import ObjectId
from flask import Blueprint, jsonify, request, send_from_directory
from flask.globals import session
from flask_api.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_409_CONFLICT, HTTP_403_FORBIDDEN
from flask_login import login_required, current_user

from api import user
from api.common import get_request_data
from extentions import LoyalityJSONDecoder
from models.host import Host, OWNER_UID, TITLE, DESCRIPTION, ADDRESS, TIME_OPEN, TIME_CLOSE, LOYALITY_TYPE, \
    LOYALITY_PARAM
from models.score import Score
from models.user import User

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
    owner = User(uid=current_user.uid)
    if owner.workplace_uid is not None:
        return jsonify({'message': "Please retire first"}), HTTP_409_CONFLICT
    host = Host(data)
    host_uid = host.save()
    if host_uid is None:
        return jsonify({'message': "Host with this title (and owner) already exists"}), HTTP_409_CONFLICT
    owner.workplace_uid = session['host_id'] = host_uid
    owner.save()
    return jsonify({'code': 0, 'host_id': host_uid, 'message': 'OK'})


@host_bp.route('get_client/', methods=['GET'])
@login_required
def get_client_score():
    data = get_request_data(request)
    client_id = data.get('client_id')
    if client_id is None:
        return jsonify({'message': "client_id required"}), HTTP_400_BAD_REQUEST
    host_id = session.get('host_id')
    if host_id is None:
        return jsonify({'message': "Please login as a staff"}), HTTP_403_FORBIDDEN
    score = Score(host_id, client_id).score
    if score is None:
        return jsonify({'message': "No host with this id"}), HTTP_404_NOT_FOUND
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
    """If host_id provided returns that host info elif host_id in session returns your host info else 400"""
    host_id = get_request_data(request).get('host_id') or session.get('host_id')
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
    host_uid = session.get('host_id')
    if not host_uid:
        return jsonify({'message': "Not logged in"}), HTTP_403_FORBIDDEN
    data = get_request_data(request)
    if not data.get(TITLE):
        return jsonify({'message': "Title required"}), HTTP_400_BAD_REQUEST
    host = Host(uid=host_uid)
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
    """Loyality update. loyality_type and loyality_param required"""
    data = get_request_data(request, cls=LoyalityJSONDecoder)
    host_uid = session.get('host_id')
    if not host_uid:
        return jsonify({'message': "Please log in as owner"}), HTTP_403_FORBIDDEN
    loyality_type, loyality_param = data.get(LOYALITY_TYPE), data.get(LOYALITY_PARAM)
    if not Host.check_loyality(loyality_type, loyality_param):
        return jsonify({'message': "Loyality is wrong"}), HTTP_400_BAD_REQUEST
    host = Host(uid=host_uid)
    if current_user.uid != host.owner_uid:
        return jsonify({'message': "You are not owner of this host"}), HTTP_403_FORBIDDEN
    host.change_loyality(loyality_type, loyality_param)
    return jsonify(SUCCESS)


@host_bp.route('delete/', methods=['POST'])
@login_required
def delete_host():
    host_uid = session.get('host_id')
    if not host_uid:
        return jsonify({'message': "Please login as owner"}), HTTP_403_FORBIDDEN
    host = Host(uid=host_uid)
    if host.uid is None:
        return jsonify({'message': "No host with uid="+host_uid+" in db"}), HTTP_404_NOT_FOUND
    if current_user.uid != host.owner_uid:
        return jsonify({'message': "You are not this host"}), HTTP_403_FORBIDDEN
    User.retire(host.staff_uids.difference([host.owner_uid]))
    host.delete()
    return jsonify({'code': 0})


@host_bp.route('get_staff/', methods=['POST'])
@login_required
def get_staff():
    host_uid = session.get('host_id')
    if host_uid is None:
        return jsonify({'message': "Please log in as owner"}), HTTP_403_FORBIDDEN
    host = Host(uid=host_uid)
    if current_user.uid != host.owner_uid:
        return jsonify({'message': "Please log in as owner"}), HTTP_403_FORBIDDEN
    workers = host.get_staff()
    return jsonify({'code': 0, 'staff': workers})


@host_bp.route('hire/', methods=['POST'])
@login_required
def hire():
    """worker_id required"""
    host_uid = session.get('host_id')
    if host_uid is None:
        return jsonify({'message': "You need to be an owner"}), HTTP_403_FORBIDDEN
    data = get_request_data(request)
    worker_uid = data.get('worker_id')
    if worker_uid is None or not ObjectId.is_valid(worker_uid):
        return jsonify({'message': "worker_id required"}), HTTP_400_BAD_REQUEST
    worker = User(uid=worker_uid)
    if worker.login is None:
        return jsonify({'message': "No such user"}), HTTP_404_NOT_FOUND
    if worker.workplace_uid is not None:
        return jsonify({'message': "This user is occupied"}), HTTP_409_CONFLICT
    host = Host(uid=host_uid)
    if current_user.uid != host.owner_uid:
        return jsonify({'message': "You are not owner of this host"}), HTTP_403_FORBIDDEN
    host.hire(worker_uid)
    worker.workplace_uid = host_uid
    worker.save()
    return jsonify(SUCCESS)

@host_bp.route('retire/', methods=['POST'])
@login_required
def retire():
    """worker_id required"""
    host_uid = session.get('host_id')
    if host_uid is None:
        return jsonify({'message': "You need to be an owner"}), HTTP_403_FORBIDDEN
    data = get_request_data(request)
    worker_uid = data.get('worker_id')
    if not worker_uid or not ObjectId.is_valid(worker_uid):
        return jsonify({'message': "worker_id required"}), HTTP_400_BAD_REQUEST
    host = Host(uid=host_uid)
    if current_user.uid != host.owner_uid:
        return jsonify({'message': "You are not owner of this host"}), HTTP_403_FORBIDDEN
    if host.owner_uid == ObjectId(worker_uid):
        return jsonify({'message': "You can't retire yourself"}), HTTP_409_CONFLICT
    if ObjectId(worker_uid) not in host.staff_uids:
        return jsonify({'message': "No such worker"}), HTTP_404_NOT_FOUND
    worker_uid = host.retire(worker_uid)
    User.retire(worker_uid)
    return jsonify(SUCCESS)


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
