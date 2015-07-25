# -*- coding: utf-8 -*-

from ..core import jwt
from ..models import User
import datetime



@jwt.authentication_handler
def login(username, password):
    user = User.query.filter_by(username=username).one()
    if user.check_password(password):
        return user


@jwt.user_handler
def load_user(payload):
    user = User.query.get(payload['user_id'])
    print(user)
    if user:
        return user
    return None


@jwt.payload_handler
def make_payload(user):
    return {
        'user_id': str(user.id),
        'exp': (
            datetime.datetime.utcnow().timestamp()
        )
    }
