from flask import Flask, session, jsonify, request, redirect, url_for
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.contrib.fixers import ProxyFix
from werkzeug.utils import secure_filename

from models.user.User import User
from models.shop.Shop import Shop

UPLOAD_FOLDER = '/static/'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.secret_key = 'Afe454_gjklr993mkl2nFsdfGRrrggReQcBmm'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

lm = LoginManager()
lm.init_app(app)

test_user = User('test_user', 'password')
clients = list()
shops = list()

i = 0
while i < 10:
	shops.append(Shop(iD = i, title = "shop" + str(i), description = "Best cafe" + str(i)))
	i = i + 1

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

@app.route('/api/client/register/', methods=['POST'])
def register():
    data = dict((k, v) for (k, v) in request.json.items())
    login = data.get('login', None)
    password = data.get('password', None)
    if login != None and password != None:
    	for user in clients:
    		if user.login == login:
    			return jsonify({ 'code': 1, 'message': 'already registered' })
    	clients.append(User(login,password))
        return jsonify({ 'code': 0, 'message': 'you are registered' })
    return jsonify({ 'code': 1, 'message': 'wrong login/password' })

@app.route('/api/client/login/', methods=['POST'])
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
    			return jsonify({ 'code': 0, 'message': 'already logged in' })
    		else:
    			return jsonify({ 'code': 1, 'message': 'already logged in as another' })
    	user = User(login, password)
    	login_user(user)
        session['username'] = login
        return jsonify({ 'code': 0, 'message': 'logged in' })
    return jsonify({ 'code': 1, 'message': 'wrong credentials' })

@app.route('/api/client/list_hosts/', methods=['GET'])
@login_required
def get_shops():
	shopList = list()
	for shop in shops:
		shopDict = {"title": shop.title, "description": shop.description, "logo": shop.logo}
		shopList.append(shopDict)
	return jsonify({ 'code': 0, 'hosts':  shopList})

@app.route('/', methods=['GET'])
def upload_file():
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('uploaded_file',
                                    filename=filename))

if __name__ == '__main__':
    app.run(host='0.0.0.0')

