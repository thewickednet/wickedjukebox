# -*- coding: utf-8 -*-

import os

from config_resolver import Config
from flask import Flask

from .core import db, login_manager, jwt, cors
from .helpers import register_blueprints
from .middleware import HTTPMethodOverrideMiddleware
from .services import user


def create_app(package_name, package_path, settings_override=None):
    """Returns a :class:`Flask` application instance configured with common
    functionality for the Jukebox platform.

    :param package_name: application package name
    :param package_path: application package path
    :param settings_override: a dictionary of settings to override
    """
    app = Flask(package_name, instance_path=os.getcwd(), instance_relative_config=True)
    app.localconfig = Config('wicked', 'jukebox', version='1.0', require_load=True)
    app.config.from_object('jukebox.settings')

    for option in app.localconfig.options('flask'):
        app.config[option.upper()] = app.localconfig.get('flask', option)

    db.init_app(app)
    jwt.init_app(app)
    login_manager.init_app(app)
    cors.init_app(app)
    login_manager.login_view = '/login'

    register_blueprints(app, package_name, package_path)

    app.wsgi_app = HTTPMethodOverrideMiddleware(app.wsgi_app)

    @login_manager.user_loader
    def load_user(userid):
        return user.get(userid)

    return app
