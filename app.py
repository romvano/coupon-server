from flask import Flask
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

from models import User
from api.host import host

app = Flask(__name__)
app.config.from_object('config')
app.secret_key = 'Afe454_gjklr993mkl2nFsdfGRrrggReQcBmm'

# configure login manager
lm = LoginManager()
lm.init_app(app)

app.register_blueprint(host, url_prefix='/api/host/')
app.register_blueprint(host, url_prefix='/api/barmen/')

@lm.user_loader
def load_user(id):
    return User('test_user', 'password')

if __name__ == '__main__':
    app.run()