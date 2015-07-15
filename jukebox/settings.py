# -*- coding: utf-8 -*-

DEBUG = True
SECRET_KEY = 'super-secret-key'

SQLALCHEMY_DATABASE_URI = 'mysql+oursql://jukebox@localhost:3306/jukebox'

SECURITY_POST_LOGIN_VIEW = '/'
SECURITY_PASSWORD_HASH = 'plaintext'
SECURITY_PASSWORD_SALT = 'password_salt'
SECURITY_REMEMBER_SALT = 'remember_salt'
SECURITY_RESET_SALT = 'reset_salt'
SECURITY_RESET_WITHIN = '5 days'
SECURITY_CONFIRM_WITHIN = '5 days'
SECURITY_SEND_REGISTER_EMAIL = False
