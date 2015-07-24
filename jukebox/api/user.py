# -*- coding: utf-8 -*-

from flask import Blueprint
from flask_jwt import current_user

from ..services import user
from . import route

bp = Blueprint('user', __name__, url_prefix='/user')


@route(bp, '/<user_id>')
def show(user_id):
    """Returns an artist instance."""
    return user.get_or_404(user_id)


@route(bp, '/current')
def current():
    """Returns an artist instance."""
    print(type(current_user))
    return current_user
