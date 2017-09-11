from flask import Flask
from flask_login import LoginManager

from api.host import host_bp
from api.client import client_bp
from api.user import user_bp
from extentions import setup, mongo, lm, JSONEncoder
import config

app = Flask(__name__)
app.config.from_object(config)
app.json_encoder = JSONEncoder

app.secret_key = 'Afe454_gjklr993mkl2nFsdfGRrrggReQcBmm'

app.register_blueprint(host_bp, url_prefix='/api/host/')
app.register_blueprint(host_bp, url_prefix='/api/barmen/')
app.register_blueprint(client_bp, url_prefix='/api/client/')
app.register_blueprint(user_bp, url_prefix='api/user/')

lm.init_app(app)

mongo.init_app(app)
# setup(mongo)

if __name__ == '__main__':
    app.run(host='0.0.0.0', threaded=True)
