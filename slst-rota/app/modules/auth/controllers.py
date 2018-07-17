from flask import Blueprint, request, render_template, flash, session, redirect, url_for  # Flask
from werkzeug.security import check_password_hash, generate_password_hash  # Passwords
from typing import Union  # Typing

from app import db_session, error_render  # DB, Errors
from app.modules.auth.forms import LoginForm  # Forms
from app.modules.auth.models import User  # Models

# Blueprint
auth = Blueprint('auth', __name__, url_prefix='/auth')


def current_user() -> Union[None, User]:
    if session and 'user_id' in session and session['user_id']:
        user = User.query.filter_by(id=session['user_id']).first()
        if user:
            return user
    return None


# Login
@auth.route('/login/', methods=['GET', 'POST'])
def login():
    # If session exists
    if current_user():
        return error_render(500)

    # If sign in form is submitted
    form = LoginForm(request.form)

    # Verify the sign in form
    if form.validate_on_submit():

        user = User.query.filter_by(username=form.username.data).first()

        if user and check_password_hash(user.password, form.password.data):
            session['user_id'] = user.id

            return redirect(url_for('index'))

        flash('Wrong email or password', 'error-message')

    return render_template("auth/login.jinja2", form=form)


# Logout
@auth.route('/logout/', methods=['GET'])
def logout():
    # If session exists
    if current_user():
        session.clear()

    return redirect(url_for('index'))


# Create a dummy account
@auth.route('/dummy/student/', methods=['GET'])
def dummy_student():
    user = User("test_student", generate_password_hash("test"), 1)
    session = db_session()
    session.add(user)
    session.commit()


# Create a dummy account
@auth.route('/dummy/staff/', methods=['GET'])
def dummy_staff():
    user = User("test_staff", generate_password_hash("test"), 2)
    session = db_session()
    session.add(user)
    session.commit()
