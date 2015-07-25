
from flask import Blueprint, render_template, flash, session, redirect
from flask_login import login_user, logout_user

from . import route
from ..forms import LoginForm

bp = Blueprint('auth', __name__)


@route(bp, '/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        login_user(form.user)
        flash(u'Successfully logged in as %s' % form.user.username)
        session['user_id'] = form.user.id
        return redirect('/')
    return render_template('login.html', form=form)


@route(bp, '/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    return redirect('/')
