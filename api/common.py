import json
from extentions import lm
from models.user import User


@lm.user_loader
def load_user(uid):
    return User(uid=uid)


def get_request_data(request):
    if request.method == 'POST':
        if request.json is None:
            data = json.loads(request.data)
        else:
            data = dict((k, v) for (k, v) in request.json.items())
        return data
    if request.method == 'GET':
        data = dict((k, v) for (k, v) in request.args.items())
        return data