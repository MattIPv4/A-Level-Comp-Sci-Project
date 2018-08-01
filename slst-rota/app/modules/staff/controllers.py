from flask import Blueprint, render_template, redirect, url_for, request, flash  # Flask
from werkzeug.security import generate_password_hash  # Passwords
import calendar # Calendar

from app import db_session, error_render  # DB, Errors
from app.modules import auth  # Auth
from app.modules.staff.forms import AccountForm  # Forms
from app.modules.student import Session # Session
from app.modules.auth import User # User

# Blueprint
__a = [

]  # Convince pycharm things are used (and stop warnings)
staff = Blueprint('staff', __name__, url_prefix='/staff')


# Standard check for all routes
def auth_check():
    user = auth.current_user()
    error = None

    # If no session exists
    if not error and not user:
        error = redirect(url_for('auth.login'))

    # If not staff
    if not error and user.auth_level != 2:
        error = error_render("Staff access only",
                             "This page is only accessible to users with the staff authentication level")

    return user, error

# All accounts
@staff.route('/accounts/', methods=['GET'])
def accounts():
    user, error = auth_check()
    if error:
        return error

    data = User.query.all()
    accounts = []
    for item in data:
        accounts.append([
            item.id == user.id,
            [
                item.username,
                "{} ({})".format(item.auth_label, item.auth_level),
                "Yes" if item.disabled == 1 else "No",
                "<a href='{}' class='button'>Edit</a>".format(url_for("auth.account", id=item.id))
            ]
        ])

    return render_template("staff/accounts.jinja2", accounts=accounts)


# Create Account
@staff.route('/accounts/new', methods=['GET', 'POST'])
def new_account():
    user, error = auth_check()
    if error:
        return error

    # Form
    form = AccountForm(request.form)

    # Verify the form
    if form.validate_on_submit():

        # Verify username
        if form.username.data:

            result = User.query.filter_by(username=form.username.data).first()

            # Verify username not already used
            if not result:

                # Verify password
                if form.password.data:

                    # Verify auth level
                    if form.auth_level.data:

                        session = db_session()
                        user = User(form.username.data, generate_password_hash(form.password.data), form.auth_level.data)
                        session.add(user)
                        session.commit()
                        return redirect(url_for('staff.accounts'))

                    else:
                        flash('Please select an auth level')

                else:
                    flash('Please enter a password')

            else:
                flash('Username {} already in use'.format(form.username.data))

        else:
            flash('Please enter a username')

    # Render
    return render_template("staff/new_account.jinja2", form=form)


# Rota view
@staff.route('/rota/', methods=['GET'])
def rota():
    user, error = auth_check()
    if error:
        return error

    # Get rota data
    data = Session.query.filter_by(archived=False).order_by(Session.day.asc(), Session.start_time.asc()).all()
    rota_data = []
    current_day = None
    for session in data:
        # Day subheadings
        if session.day != current_day:
            rota_data.append([False, [list(calendar.day_name)[session.day], "", "", ""]])
            current_day = session.day

        # Assignments for day (highlight ones with current user)
        rota_data.append([
            (session.assignments == []),
            [
                session.start_time_frmt,
                session.end_time_frmt,
                ", ".join([f.user.username for f in session.assignments]) or "None",
                "<a href='{}' class='button'>Edit Session</a>".format(url_for("staff.rota_edit_session", id=session.id)) +
                " &nbsp; <a href='{}' class='button'>Update Assignments</a>".format(url_for("staff.rota_edit_assignments", id=session.id))
            ]
        ])

    return render_template("staff/rota.jinja2", rota_data=rota_data)

# Rota edit - session
@staff.route('/rota/edit/session/<int:id>', methods=['GET', 'POST'])
def rota_edit_session(id: int):
    user, error = auth_check()
    if error:
        return error

    ## TODO: below

# Rota edit - assignments
@staff.route('/rota/edit/assignments/<int:id>', methods=['GET', 'POST'])
def rota_edit_assignments(id: int):
    user, error = auth_check()
    if error:
        return error

    ## TODO: below


# New rota session
@staff.route('/rota/new', methods=['GET', 'POST'])
def rota_new():
    user, error = auth_check()
    if error:
        return error

    ## TODO: below

    # Form
    form = AccountForm(request.form)

    # Verify the form
    if form.validate_on_submit():

        # Verify username
        if form.username.data:

            result = User.query.filter_by(username=form.username.data).first()

            # Verify username not already used
            if not result:

                # Verify password
                if form.password.data:

                    # Verify auth level
                    if form.auth_level.data:

                        session = db_session()
                        user = User(form.username.data, generate_password_hash(form.password.data), form.auth_level.data)
                        session.add(user)
                        session.commit()
                        return redirect(url_for('staff.accounts'))

                    else:
                        flash('Please select an auth level')

                else:
                    flash('Please enter a password')

            else:
                flash('Username {} already in use'.format(form.username.data))

        else:
            flash('Please enter a username')

    # Render
    return render_template("staff/new_account.jinja2", form=form)