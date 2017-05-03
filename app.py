from flask import Flask
from flask_login import LoginManager

from models.user import User
from api.host import host_bp
from api.client import client_bp

app = Flask(__name__)
app.config.from_object('config')
app.secret_key = 'Afe454_gjklr993mkl2nFsdfGRrrggReQcBmm'

app.register_blueprint(host_bp, url_prefix='/api/host/')
app.register_blueprint(host_bp, url_prefix='/api/barmen/')
app.register_blueprint(client_bp, url_prefix='/api/client/')

lm = LoginManager()
lm.init_app(app)

@lm.user_loader
def load_user(id):
    return User('test_user', 'password')

if __name__ == '__main__':
    app.run(host='0.0.0.0')
