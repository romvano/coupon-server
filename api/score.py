from functools import wraps

from flask.blueprints import Blueprint
from flask.globals import request, session
from flask.json import jsonify
from flask_api.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_403_FORBIDDEN
from flask_login.utils import login_required, current_user

from api.common import get_request_data, get_current_host_id
from extentions import LoyalityJSONDecoder
from models.host import Host, CUP_LOYALITY, PERCENT_LOYALITY, DISCOUNT_LOYALITY
from models.score import Score
from models.user import User

score_bp = Blueprint('score_bp', __name__)

def check_400(f):
    @wraps(f)
    def checking():
        data = get_request_data(request, cls=LoyalityJSONDecoder)
        host_uid = get_current_host_id()
        if not host_uid:
            return jsonify({'message': "You need to be a staff"}), HTTP_403_FORBIDDEN
        user_uid = data.get('user_id')
        if not user_uid:
            return jsonify({'message': "No user_id provided"}), HTTP_400_BAD_REQUEST
        score_update = data['score'] if data.get('score') else None
        if not score_update or not (isinstance(score_update, int) or isinstance(score_update, float)):
            return jsonify({'message': "Score value is invalid"}), HTTP_400_BAD_REQUEST
        host = Host(uid=host_uid)
        if host.uid is None:
            return jsonify({'message': "No such host"}), HTTP_404_NOT_FOUND
        if not host.check_loyality(host.loyality_type, host.loyality_param):
            return jsonify({'code': 2, 'message': "Loyality of the host is not set"})
        if current_user.uid not in host.staff_uids:
            return jsonify({'message': "You are not a staff of this place"}), HTTP_403_FORBIDDEN
        user = User(uid=user_uid)
        if user.login is None:
            return jsonify({'message': "No such user"}), HTTP_404_NOT_FOUND
        score = Score(host.uid, user.uid)
        return f(host, user, score, score_update)
    return checking


@score_bp.route('cup/', methods=['POST'])
@login_required
@check_400
def cup(host, user, score, score_update):
    """Update points for 'cup' loyality program"""
    if host.loyality_type != CUP_LOYALITY or not Host.check_loyality(host.loyality_type, host.loyality_param):
        return jsonify({'message': "Wrong loyality type"}), HTTP_403_FORBIDDEN
    # increasing points
    if score_update == 1:
        print score.score
        score.score += 1
        score.save()
        return jsonify({'code': 0, 'score': score.score, 'free': host.loyality_param, 'message': "Plus one point"})
    # decreasing points
    if score_update == -1:
        if score.score < host.loyality_param:
            return jsonify({'code': 1, 'score': score.score, 'free': host.loyality_param, 'message': "Not enough cups"})
        score.score -= host.loyality_param
        score.save()
        return jsonify({'code': 0, 'score': score.score, 'free': host.loyality_param, 'message': "Minus cup"})
    return jsonify({'message': "Wrong value for update"}), HTTP_400_BAD_REQUEST


@score_bp.route('percent/', methods=['POST'])
@login_required
@check_400
def percent(host, user, score, score_update):
    """Update points for 'percent' loyality program"""
    if host.loyality_type != PERCENT_LOYALITY or not Host.check_loyality(host.loyality_type, host.loyality_param):
        return jsonify({'message': "Wrong loyality type"}), HTTP_403_FORBIDDEN
    # increasing points
    if score_update >= 0:
        score.score += float(score_update * host.loyality_param) / 100
        score.save()
        return jsonify({'code': 0, 'score': score.score, 'message': "Score increased"})
    # decreasing points
    if score_update < 0:
        if score.score < abs(score_update):
            return jsonify({'code': 1, 'score': score.score, 'message': "Not enough bonuses"})
        score.score -= abs(score_update)
        score.save()
        return jsonify({'code': 0, 'score': score.score, 'message': "Score decreased"})
    return jsonify({'message': "Wrong value for update"}), HTTP_400_BAD_REQUEST

@score_bp.route('discount/', methods=['POST'])
@login_required
@check_400
def discount(host, user, score, score_update):
    """Update points for 'discount' loyality program"""
    if host.loyality_type != DISCOUNT_LOYALITY or not Host.check_loyality(host.loyality_type, host.loyality_param):
        return jsonify({'message': "Wrong loyality type"}), HTTP_403_FORBIDDEN
    # increasing points
    if score_update <= 0:
        return jsonify({'message': "Wrong value for update"}), HTTP_400_BAD_REQUEST
    discount = score.get_discount()
    counted_score = score_update - score_update * discount
    score.score += counted_score
    score.save()
    return jsonify({'code': 0, 'score': score.score, 'discount': discount, 'message': "Updated"})
