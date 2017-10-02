# -*- coding: utf-8 -*-

from flask import Flask

from api.host import host_bp
from api.client import client_bp
from api.score import score_bp
from api.user import user_bp
from extentions import mongo, lm, JSONEncoder
import config

app = Flask(__name__)
app.config.from_object(config)
app.json_encoder = JSONEncoder

app.secret_key = 'Afe454_gjklr993mkl2nFsdfGRrrggReQcBmm'

lm.init_app(app)

mongo.init_app(app)

app.register_blueprint(host_bp, url_prefix='/api/host/')
app.register_blueprint(host_bp, url_prefix='/api/barmen/')
app.register_blueprint(client_bp, url_prefix='/api/client/')
app.register_blueprint(user_bp, url_prefix='/api/user/')
app.register_blueprint(score_bp, url_prefix='/api/score/')


if __name__ == '__main__':
    app.run(host='0.0.0.0', threaded=True)
