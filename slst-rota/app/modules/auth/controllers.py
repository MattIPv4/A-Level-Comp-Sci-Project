from typing import Union  # Typing

from flask import Blueprint, request, render_template, flash, session, redirect, url_for  # Flask
from werkzeug.security import check_password_hash, generate_password_hash  # Passwords

from app import db_session, error_render  # DB, Errors
from app.modules.auth.forms import LoginForm, AccountForm  # Forms
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
        return redirect(url_for('index'))

    # If sign in form is submitted
    form = LoginForm(request.form)

    # Verify the sign in form
    if form.validate_on_submit():

        user = User.query.filter_by(disabled=0, username=form.username.data).first()

        if user and check_password_hash(user.password, form.password.data):
            session['user_id'] = user.id

            return redirect(url_for('index'))

        flash('Wrong username or password')

    return render_template("auth/login.jinja2", form=form)


# Logout
@auth.route('/logout/', methods=['GET'])
def logout():
    # If session exists
    if current_user():
        session.clear()

    return redirect(url_for('index'))


# Manage Account
@auth.route('/account/', methods=['GET', 'POST'])
@auth.route('/account/<int:id>', methods=['GET', 'POST'])
def account(id: int = None):
    user = current_user()

    # If no session exists
    if not user:
        return redirect(url_for('auth.login'))

    # Set default target
    target = user

    # If attempting to edit another account
    if id is not None:
        if user.auth_level != 2:
            return error_render("Staff access only", "Editing of other accounts is restricted to staff users only.")

        result = User.query.filter_by(id=id).first()
        if not result:
            return error_render("Account not found", "An account with the id {} was not found.".format(id))

        target = result

    # Form
    form = AccountForm(request.form)

    # Verify the form
    if form.validate_on_submit():

        dbsession = db_session()

        # Handle username change
        if form.username.data != target.username:

            # Ensure correct access
            if user.auth_level == 2:

                # Verify username
                if form.username.data:

                    result = User.query.filter_by(username=form.username.data).first()
                    # Verify username not already used
                    if not result:

                        # Update username
                        user_session = User.query.with_session(dbsession).filter_by(id=target.id).first()
                        user_session.username = form.username.data
                        target.username = form.username.data
                        dbsession.commit()
                        flash('Username updated')

                    else:
                        flash('Username {} already in use'.format(form.username.data))

                else:
                    flash('Please enter a username')

            else:
                flash('Invalid access to update username')

        # Handle auth level change
        if form.auth_level.data != target.auth_level:

            # Ensure correct access
            if user.auth_level == 2 and target.id != user.id:

                # Update username
                user_session = User.query.with_session(dbsession).filter_by(id=target.id).first()
                user_session.auth_level = form.auth_level.data
                target.auth_level = form.auth_level.data
                dbsession.commit()
                flash('Auth level updated')

            else:
                flash('Invalid access to update auth level')

        # Handle disabled change
        if form.disabled.data != target.disabled:

            # Ensure correct access
            if user.auth_level == 2 and target.id != user.id:

                # Update username
                user_session = User.query.with_session(dbsession).filter_by(id=target.id).first()
                user_session.disabled = form.disabled.data
                target.disabled = form.disabled.data
                dbsession.commit()
                flash('Disabled status updated')

            else:
                flash('Invalid access to update disabled status')

        # Handle password change
        if form.new_password.data:

            # Ensure correct access
            if target.id == user.id or user.auth_level == 2:

                # Verify new = new confirm
                if form.new_password.data == form.new_password_confirm.data:

                    # Verify old = current, or skip if not editing current user
                    if target.id != user.id or check_password_hash(user.password, form.old_password.data):

                        # Update password
                        user_session = User.query.with_session(dbsession).filter_by(id=target.id).first()
                        user_session.password = generate_password_hash(form.new_password.data)
                        target.password = generate_password_hash(form.new_password.data)
                        dbsession.commit()
                        flash('Password updated')

                    else:
                        flash('Old Password is not correct')

                else:
                    flash('New Password and New Password Confirmation do not match')

            else:
                flash('Invalid access to update password')

    # Inject some values
    if target:
        form.username.data = target.username
        form.auth_level.data = target.auth_level
        form.disabled.data = target.disabled

    # Render
    return render_template("auth/account.jinja2", form=form, target=target,
                           show_auth_level=(user.auth_level == 2 and user.id != target.id),
                           show_username=(user.auth_level == 2),
                           show_old_password=(user.id == target.id))
