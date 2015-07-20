# -*- coding: utf-8 -*-

from ..core import jwt
from ..models import User
import datetime

@jwt.authentication_handler
def login(username, password):
    if username == 'joe' and password == 'pass':
        u = User(id=1, username='joe', fullname='John Doe')
        print(u)
        return u


@jwt.user_handler
def load_user(payload):
    user = User.query.get(payload['user_id'])
    print(user)
    if user:
        return user
    return {'error': 'Houston, we have a problem!'}


@jwt.payload_handler
def make_payload(user):
    return {
        'user_id': str(user.id),
        'exp': (
            datetime.datetime.utcnow().timestamp()
        )
    }
