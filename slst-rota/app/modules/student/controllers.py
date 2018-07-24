import calendar  # Calendar
from datetime import datetime  # Datetime

from flask import Blueprint, request, render_template, flash, redirect, url_for  # Flask

from app import db_session, error_render, Utils  # DB, Errors
from app.modules import auth  # Auth
from app.modules.student.forms import UnavailabilityForm  # Form
from app.modules.student.models import Session, session_to_rota_view, Unavailability  # Rota Sessions

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
    data = Session.query.filter_by(archived=False).order_by(Session.day.asc(), Session.start_time.asc()).all()
    data = [f for f in data if user.id in [g.user.id for g in f.assignments]]
    next_session = data[0]
    for session in data:
        # Session can't be before now (day)
        if session.day < datetime.today().weekday():
            continue

        # Assignment can't be before now (end time)
        if session.end_time < Utils.minutes_now():
            continue

        next_session = session
        break

    # Format for table macro
    session_is_current = False
    if next_session.day == datetime.today().weekday() \
            and next_session.start_time <= Utils.minutes_now() \
            and next_session.end_time >= Utils.minutes_now():
        session_is_current = True

    next_session = [
        session_is_current,
        [
            next_session.day_frmt,
            next_session.start_time_frmt,
            next_session.end_time_frmt,
            ", ".join([f.user.username for f in next_session.assignments])
        ]
    ]

    # Get unavailability
    data = Session.query.all()
    data2 = Unavailability.query.filter_by(user_id=user.id).all()
    unavailability_stat = "Unavailable {} / {} sessions.<br/>({:.2f}% availability)".format(
        len(data2), len(data), (1 - (len(data2) / len(data))) * 100)

    return render_template("student/index.jinja2", session_is_current=session_is_current, next_session=next_session,
                           unavailability_stat=unavailability_stat)


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
        rota_data.append(session_to_rota_view(session, lambda a: a.session.day == datetime.today().weekday()))

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
        rota_data.append(session_to_rota_view(session, lambda a: a.user.id == user.id))

    return render_template("student/rota.jinja2", title="Full rota view",
                           rota_data=rota_data, show_rota_full=False)


# Rota
@student.route('/fake/', methods=['GET'])
def fake():
    session = db_session()
    # this_fake = Session(0, 705, 735)
    # session.add(this_fake)
    # this_fake = Assignment(1, 2)
    # session.add(this_fake)
    session.commit()


# Unavailability
@student.route('/unavailability/', methods=['GET'])
def unavailability():
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

        # Don't show assigned sessions
        assigned = False
        if user.id in [f.user.id for f in session.assignments]:
            assigned = True

        # Day subheadings
        if session.day != current_day:
            rota_data.append([False, [list(calendar.day_name)[session.day], "", "", ""]])
            current_day = session.day

        # Sessions
        rota_data.append([
            False,
            [
                session.start_time_frmt,
                session.end_time_frmt,
                "Yes" if user.id in [f.user.id for f in session.unavailabilities] else "No",
                "Currently assigned, unable to update." if assigned else
                '<a class="button button-primary mbt-0" href="{}">Update unavailability</a>'.format(
                    url_for('student.unavailability_edit', id=session.id))
            ]
        ])

    return render_template("student/unavailability.jinja2", rota_data=rota_data)


# Unavailability
@student.route('/unavailability/edit/<int:id>', methods=['GET', 'POST'])
def unavailability_edit(id: int):
    user = auth.current_user()

    # If no session exists
    if not user:
        return redirect(url_for('auth.login'))

    # If not student
    if user.auth_level != 1:
        return error_render("Student access only",
                            "This page is only accessible to users with the student authentication level")

    session = Session.query.filter_by(id=id).first()

    # If bad session
    if not session or session.archived is True:
        return redirect(url_for('student.unavailability'))

    # If student assigned
    if user.id in [f.user.id for f in session.assignments]:
        return error_render("Currently assigned to session",
                            "You cannot update your unavailability on a session you are currently assigned to."
                            "\nPlease seek help from a staff user to un-assign you from the session")

    # Form
    form = UnavailabilityForm(request.form)

    # Verify the form
    if form.validate_on_submit():

        dbsession = db_session()

        if not form.unavailable.data:
            Unavailability.query.with_session(dbsession).filter_by(user_id=user.id, session_id=session.id).delete()

            dbsession.commit()
            return redirect(url_for('student.unavailability'))

        if form.unavailable.data and form.reason.data:
            Unavailability.query.with_session(dbsession).filter_by(user_id=user.id, session_id=session.id).delete()

            new_unavailablity = Unavailability(user.id, session.id, form.reason.data)
            dbsession.add(new_unavailablity)

            dbsession.commit()
            return redirect(url_for('student.unavailability'))

        flash('Please enter a reason for marking yourself as unavailable', 'error-message')

    # Get current if any
    data = Unavailability.query.filter_by(user_id=user.id, session_id=session.id).first()
    if data:
        form.unavailable.data = True
        form.reason.data = data.reason

    # Render
    return render_template("student/unavailability_edit.jinja2", form=form)
