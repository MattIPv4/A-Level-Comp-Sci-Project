from flask import Blueprint, request, render_template, flash, session, redirect, url_for  # Flask
import calendar  # Calendar
from datetime import datetime  # Datetime

from app import db_session, error_render  # DB, Errors
from app.modules import auth  # Auth
from app.modules.student.models import Session, Assignment, session_to_view  # Rota Sessions

# Blueprint
student = Blueprint('student', __name__, url_prefix='/student')


# Home
@student.route('/', methods=['GET'])
def home():
    user = auth.current_user()

    # If no session exists
    if not user:
        return redirect(url_for('auth.login'))

    # If not student
    if user.auth_level != 1:
        return error_render("Student access only",
                            "This page is only accessible to users with the student authentication level")

    # Get next session for student
    data = Session.query.order_by(Session.day.asc(), Session.start_time.asc()).all()
    data = [f for f in data if user.id in [g.user.id for g in f.assignments]]
    next_session = data[0]
    for session in data:
        # Session can't be before now (day)
        if session.day < datetime.today().weekday():
            continue

        # Assignment can't be before now (end time)
        if session.end_time < ((datetime.now() - datetime.now().replace(hour=0, minute=0, second=0,
                                                                        microsecond=0)).total_seconds() / 60):
            continue

        next_session = session
        break

    # Format for table macro
    next_session = [
        False,
        [
            next_session.day_frmt,
            next_session.start_time_frmt,
            next_session.end_time_frmt,
            ", ".join([f.user.username for f in next_session.assignments])
        ]
    ]

    return render_template("student/index.jinja2", next_session=next_session)


# Rota
@student.route('/rota/', methods=['GET'])
def rota():
    user = auth.current_user()

    # If no session exists
    if not user:
        return redirect(url_for('auth.login'))

    # If not student
    if user.auth_level != 1:
        return error_render("Student access only",
                            "This page is only accessible to users with the student authentication level")

    # Get rota data
    data = Session.query.order_by(Session.day.asc(), Session.start_time.asc()).all()
    rota_data = []
    current_day = None
    for session in data:
        # Only current user
        if user.id not in [f.user.id for f in session.assignments]:
            continue

        # Day subheadings
        if session.day != current_day:
            rota_data.append([False, [list(calendar.day_name)[session.day], "", ""]])
            current_day = session.day

        # Assignments for day
        rota_data.append(session_to_view(session, lambda a: a.session.day == datetime.today().weekday()))

    return render_template("student/rota.jinja2", title="Rota view for {}".format(user.username),
                           rota_data=rota_data, show_rota_full=True)


# Full Rota
@student.route('/rota/full/', methods=['GET'])
def rota_full():
    user = auth.current_user()

    # If no session exists
    if not user:
        return redirect(url_for('auth.login'))

    # If not student
    if user.auth_level != 1:
        return error_render("Student access only",
                            "This page is only accessible to users with the student authentication level")

    # Get rota data
    data = Session.query.order_by(Session.day.asc(), Session.start_time.asc()).all()
    rota_data = []
    current_day = None
    for session in data:
        # Day subheadings
        if session.day != current_day:
            rota_data.append([False, [list(calendar.day_name)[session.day], "", ""]])
            current_day = session.day

        # Assignments for day (highlight ones with current user)
        rota_data.append(session_to_view(session, lambda a: a.user.id == user.id))

    return render_template("student/rota.jinja2", title="Full rota view",
                           rota_data=rota_data, show_rota_full=False)


# Rota
@student.route('/fake/', methods=['GET'])
def fake():
    this_fake = Assignment(1, 1)
    session = db_session()
    session.add(this_fake)
    session.commit()
