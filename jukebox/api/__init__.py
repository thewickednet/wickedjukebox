# -*- coding: utf-8 -*-

from functools import wraps

from flask import jsonify
from flask_jwt import jwt_required

from ..core import JukeboxError, JukeboxFormError
from ..helpers import JSONEncoder
from .. import factory


def create_app(settings_override=None, register_security_blueprint=False):
    """Returns the Jukebox API application instance"""

    app = factory.create_app(__name__, __path__, settings_override,
                             register_security_blueprint=register_security_blueprint)

    # Set the default JSON encoder
    app.json_encoder = JSONEncoder

    # Register custom error handlers
    app.errorhandler(JukeboxError)(on_jukebox_error)
    app.errorhandler(JukeboxFormError)(on_jukebox_form_error)
    app.errorhandler(404)(on_404)

    return app


def noop_dec(func):
    return func


def route(bp, *args, **kwargs):
    kwargs.setdefault('strict_slashes', False)

    def decorator(f):
        @bp.route(*args, **kwargs)
        @jwt_required()
        @wraps(f)
        def wrapper(*args, **kwargs):
            sc = 200
            rv = f(*args, **kwargs)
            if isinstance(rv, tuple):
                sc = rv[1]
                rv = rv[0]
            return jsonify(dict(data=rv)), sc
        return f

    return decorator


def on_jukebox_error(e):
    return jsonify(dict(error=e.msg)), 400


def on_jukebox_form_error(e):
    return jsonify(dict(errors=e.errors)), 400


def on_404(e):
    return jsonify(dict(error='Not found')), 404
