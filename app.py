from flask import Flask, session, jsonify, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

from models.user.User import User

app = Flask(__name__)
app.secret_key = 'Afe454_gjklr993mkl2nFsdfGRrrggReQcBmm'

# configure login manager
lm = LoginManager()
lm.init_app(app)

test_user = User('test_user', 'password')

@lm.user_loader
def load_user(id):
	return test_user

def validate_credentials(login, password):
	return login == 'test_user' and password == 'qwerty'

@app.route('/api/barmen/login/', methods=['POST'])
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

@app.route('/api/barmen/logout/', methods=['POST'])
@login_required
def logout():
	session.pop('username', None)
	logout_user()
	return jsonify({ 'code': 0 })

@app.route('/api/barmen/testsession/', methods=['GET'])
@login_required
def test_session():
	return jsonify({ 'code': 0, 'message': 'wonderful!' })

if __name__ == '__main__':
    app.run(host='0.0.0.0')
