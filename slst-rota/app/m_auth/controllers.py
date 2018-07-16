from flask import Blueprint, request, render_template, flash, session, redirect, url_for  # Flask
from werkzeug.security import check_password_hash  # Passwords

from app.m_auth.forms import LoginForm  # Forms
from app.m_auth.models import User  # Models

# Blueprint
m_auth = Blueprint('auth', __name__, url_prefix='/auth')


# Set the route and accepted methods
@m_auth.route('/login/', methods=['GET', 'POST'])
def login():
    # If sign in form is submitted
    form = LoginForm(request.form)

    # Verify the sign in form
    if form.validate_on_submit():

        user = User.query.filter_by(username=form.username.data).first()

        if user and check_password_hash(user.password, form.password.data):
            session['user_id'] = user.id

            flash('Welcome %s' % user.name)

            return redirect(url_for('auth.home'))

        flash('Wrong email or password', 'error-message')

    return render_template("auth/login.jinja2", form=form)
