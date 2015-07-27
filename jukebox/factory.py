# -*- coding: utf-8 -*-

import os

from flask import Flask

from .core import db, mail, login_manager, jwt
from .helpers import register_blueprints
from .middleware import HTTPMethodOverrideMiddleware
from .services import user

from .models import Album

def create_app(package_name, package_path, settings_override=None):
    """Returns a :class:`Flask` application instance configured with common
    functionality for the Jukebox platform.

    :param package_name: application package name
    :param package_path: application package path
    :param settings_override: a dictionary of settings to override
    """
    app = Flask(package_name, instance_path=os.getcwd(), instance_relative_config=True)
    app.config.from_object('jukebox.settings')
    app.config.from_pyfile('settings.cfg', silent=True)
    app.config.from_object(settings_override)

    db.init_app(app)
    mail.init_app(app)
    jwt.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = '/login'

    register_blueprints(app, package_name, package_path)

    app.wsgi_app = HTTPMethodOverrideMiddleware(app.wsgi_app)

    @login_manager.user_loader
    def load_user(userid):
        return user.get(userid)

    return app
