from flask import Blueprint, session, jsonify, request
from flask_login import login_required, login_user, logout_user, current_user
from models.user import User
from models.host import Host

host_bp = Blueprint('host_bp', __name__)

barmen_counter = 1
barmens = list()
barmens.append(User('test_user', 'qwerty', barmen_counter))
barmen_counter = barmen_counter + 1

while barmen_counter < 10:
    barmens.append(User('test_user' + str(barmen_counter), 'qwerty' + str(barmen_counter), barmen_counter))
    barmen_counter = barmen_counter + 1

shops = list()

i = 0
while i < 10:
    shops.append(Host(id = i, title = "shop" + str(i), description = "Best cafe" + str(i), 
        address='Pushkina', time_open='9:00', time_close='23:00', logo = 'jhdun.jpg'))
    i = i + 1

def get_id(login, password):
    for barmen in barmens:
            if barmen.login == login and barmen.password == password:
                return barmen.id
    return 0

@host_bp.route('register/', methods=['POST'])
def register():
    global barmen_counter
    data = dict((k, v) for (k, v) in request.json.items())
    login = data.get('login', None)
    password = data.get('password', None)
    if login != None and password != None:
        for barmen in barmens:
            if barmen.login == login:
                return jsonify({ 'code': 1, 'message': 'already registered' })
        barmens.append(User(login, password, barmen_counter))
        shops.append(Host())
        barmen_counter = barmen_counter + 1
        return jsonify({ 'code': 0, 'message': 'you are registered' })
    return jsonify({ 'code': 1, 'message': 'wrong login/password' })

@host_bp.route('login/', methods=['POST'])
def login():
    data = dict((k, v) for (k, v) in request.json.items())
    login = data.get('login', None)
    password = data.get('password', None)
    isHosted = False
    current_id = get_id(login, password)
    if shops[current_id].id != 0:
            isHosted = True
    if current_id != 0:
        if 'username' in session:
            if current_user and session['username'] == login:
                session.pop('username', None)
                logout_user()
                user = User(login, password)
                login_user(user)
                session['username'] = login
                return jsonify({ 'code': 0, 'message': 'You are already logged in', 'isHosted': isHosted })
            else:
                session.pop('username', None)
                logout_user()
                return jsonify({ 'code': 1, 'message': 'You are already logged in as another', 'isHosted': False})
        user = User(login, password)
        login_user(user)
        session['username'] = login
        return jsonify({ 'code': 0, 'message': 'Logged in', 'isHosted': isHosted })
    return jsonify({ 'code': 1, 'message': 'Wrong credentials', 'isHosted': False})

@host_bp.route('logout/', methods=['POST'])
@login_required
def logout():
    session.pop('username', None)
    logout_user()
    return jsonify({ 'code': 0 })

@host_bp.route('edithost/', methods=['POST'])
@login_required
def edit_host():
    data = dict((k, v) for (k, v) in request.json.items())
    current_id = data.get('id', None)
    password = data.get('password', None)
    return jsonify({ 'code': 0 })

@host_bp.route('testsession/', methods=['GET'])
@login_required
def test_session():
    return jsonify({ 'code': 0, 'message': 'wonderful!' })