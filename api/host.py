from flask import Blueprint, session, jsonify, request
from flask_login import login_required, login_user, logout_user, current_user
from models.User import User

host = Blueprint('host', __name__)

def validate_credentials(login, password):
    return login == 'test_user' and password == 'qwerty'

@host.route('login/', methods=['POST'])
def login():
    data = dict((k, v) for (k, v) in request.json.items())
    login = data.get('login', None)
    password = data.get('password', None)
    
    if validate_credentials(login, password):
        if 'username' in session:
            if current_user and session['username'] == login:
                return jsonify({ 'code': 0, 'message': 'already logged in' })
            else:
                return jsonify({ 'code': 1, 'message': 'already logged in as another' })
        user = User(login, password)
        login_user(user)
        session['username'] = login
        return jsonify({ 'code': 0, 'message': 'logged in' })
    return jsonify({ 'code': 1, 'message': 'wrong credentials' })

@host.route('logout/', methods=['POST'])
@login_required
def logout():
    session.pop('username', None)
    logout_user()
    return jsonify({ 'code': 0 })

@host.route('testsession/', methods=['GET'])
@login_required
def test_session():
    return jsonify({ 'code': 0, 'message': 'wonderful!' })