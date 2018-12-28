import calendar  # Calendar
from datetime import datetime  # Datetime
from typing import Tuple, Union  # Typing

from flask import Blueprint, request, render_template, flash, redirect, url_for  # Flask

from app import db_session, error_render, Utils  # DB, Errors
from app.modules import auth  # Auth
from app.modules.auth import User  # User
from app.modules.student.forms import UnavailabilityForm  # Form
from app.modules.student.models import Session, session_to_rota_view, Assignment, Unavailability, \
    Attendance  # Rota Sessions

# Blueprint
__a = [
    Session, Assignment, Unavailability, Attendance
]  # Convince pycharm things are used (and stop warnings)
student = Blueprint('student', __name__, url_prefix='/student')


# Standard check for all routes
def auth_check():
    user = auth.current_user()
    error = None

    # If no session exists
    if not error and not user:
        error = redirect(url_for('auth.login'))

    # If not student
    if not error and user.auth_level != 1:
        error = error_render("Student access only",
                             "This page is only accessible to users with the student authentication level")

    return user, error


# Quick method to get next/current assignment
def next_current_assignment(user: User) -> Tuple[Union[Session, None], bool]:
    # Get session assignments
    data = Session.query.filter_by(archived=False).order_by(Session.day.asc(), Session.start_time.asc()).all()
    data = [f for f in data if user.id in [g.user.id for g in f.assignments if not g.removed]]

    # Handle no assignments
    if not data:
        return None, False

    # Get next/current
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

    # Check if the next session is current
    session_is_current = False
    if next_session.day == datetime.today().weekday() \
            and next_session.start_time <= Utils.minutes_now() \
            and next_session.end_time >= Utils.minutes_now():
        session_is_current = True

    return next_session, session_is_current


# Quick method to get if a user is signed in/out for a session
def signed_in_out_session(user: User, session: Union[Session, None]) -> Tuple[Union[Attendance, None], bool, bool]:
    if not session:
        return None, False, False

    data = Attendance.query.filter_by(user_id=user.id, session_id=session.id).order_by(
        Attendance.in_time.desc()).first()

    # No attendance or not today's attendance
    if not data or data.in_time.date() != datetime.now().date():
        return data, False, False

    # If has an out time
    if data.out_time:
        return data, True, True

    # In but not out
    return data, True, False


# Home
@student.route('/', methods=['GET'])
def home():
    user, error = auth_check()
    if error:
        return error

    # Get next session for student
    next_session, session_is_current = next_current_assignment(user)

    # Format for table macro
    next_session_org = next_session
    if next_session:
        next_session = [
            session_is_current,
            [
                next_session.day_frmt,
                next_session.start_time_frmt,
                next_session.end_time_frmt,
                ", ".join([f.user.username for f in next_session.assignments if not f.removed])
            ]
        ]

    # Get unavailability
    data = Session.query.filter_by(archived=False).all()
    data2 = [f for f in Unavailability.query.filter_by(user_id=user.id).all() if not f.session.archived]
    unavailability_stat = "Unavailable {} / {} sessions.<br/>({:.2f}% availability)".format(
        len(data2), len(data), (1 - (len(data2) / len(data))) * 100)

    return render_template("student/index.jinja2", session_is_current=session_is_current, next_session=next_session,
                           unavailability_stat=unavailability_stat,
                           signed_in_out_session=signed_in_out_session(user, next_session_org))


# Rota
@student.route('/rota/', methods=['GET'])
def rota():
    user, error = auth_check()
    if error:
        return error

    # Get rota data
    data = Session.query.filter_by(archived=False).order_by(Session.day.asc(), Session.start_time.asc()).all()
    rota_data = []
    current_day = None
    for session in data:
        # Only current user
        if user.id not in [f.user.id for f in session.assignments if not f.removed]:
            continue

        # Day subheadings
        if session.day != current_day:
            rota_data.append([False, [list(calendar.day_name)[session.day], "", ""]])
            current_day = session.day

        # Assignments for day
        rota_data.append(session_to_rota_view(session, lambda a: a.session.day == datetime.today().weekday()))

    return render_template("student/rota.jinja2", title="Rota view for {}".format(user.username),
                           rota_data=rota_data, show_rota_full=True,
                           has_highlighted=bool(sum([f[0] for f in rota_data])))


# Full Rota
@student.route('/rota/full/', methods=['GET'])
def rota_full():
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
            rota_data.append([False, [list(calendar.day_name)[session.day], "", ""]])
            current_day = session.day

        # Assignments for day (highlight ones with current user)
        rota_data.append(session_to_rota_view(session, lambda a: a.user.id == user.id))

    return render_template("student/rota.jinja2", title="Full rota view",
                           rota_data=rota_data, show_rota_full=False,
                           has_highlighted=bool(sum([f[0] for f in rota_data])))


# Unavailability
@student.route('/unavailability/', methods=['GET'])
def unavailability():
    user, error = auth_check()
    if error:
        return error

    # Get rota data
    data = Session.query.filter_by(archived=False).order_by(Session.day.asc(), Session.start_time.asc()).all()
    rota_data = []
    current_day = None
    for session in data:

        # Don't show assigned sessions
        assigned = False
        if user.id in [f.user.id for f in session.assignments if not f.removed]:
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
                '<a class="button primary mbt-0" href="{}"><i class="fas fa-lg fa-edit"></i> Update unavailability</a>'
                ''.format(url_for('student.unavailability_edit', id=session.id))
            ]
        ])

    return render_template("student/unavailability.jinja2", rota_data=rota_data)


# Unavailability
@student.route('/unavailability/edit/<int:id>', methods=['GET', 'POST'])
def unavailability_edit(id: int):
    user, error = auth_check()
    if error:
        return error

    session = Session.query.filter_by(id=id).first()

    # If bad session
    if not session or session.archived is True:
        return redirect(url_for('student.unavailability'))

    # If student assigned
    if user.id in [f.user.id for f in session.assignments if not f.removed]:
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

        flash('Please enter a reason for marking yourself as unavailable')

    # Get current if any
    data = Unavailability.query.filter_by(user_id=user.id, session_id=session.id).first()
    if data:
        form.unavailable.data = True
        form.reason.data = data.reason

    # Render
    return render_template("student/unavailability_edit.jinja2", form=form)


# Sign in
@student.route('/attendance/in/', methods=['GET'])
def attendance_in():
    user, error = auth_check()
    if error:
        return error

    # Get next session for student
    next_session, session_is_current = next_current_assignment(user)

    # Handle no session
    if not next_session:
        return error_render("No assigned sessions found", "No rota sessions assigned to your user were found")

    # Handle no current session (or session further than 5 minutes away)
    if not session_is_current and (next_session.start_time - Utils.minutes_now()) > 5:
        return error_render("No current assigned session found", "No rota session assigned to your user that is current"
                                                                 " (now or less than five minutes away) was found")

    # Get most recent sign in for this session
    data = signed_in_out_session(user, next_session)

    # If already signed in
    if data[1]:
        return error_render("Already signed in for assigned session",
                            "Your user is already signed in for the current assinged session")

    # Insert attendance into db
    session = db_session()
    attendance = Attendance.from_session(user.id, next_session)
    session.add(attendance)
    session.commit()

    return redirect(url_for("index"))


# Sign out
@student.route('/attendance/out/', methods=['GET'])
def attendance_out():
    user, error = auth_check()
    if error:
        return error

    # Get next session for student
    next_session, session_is_current = next_current_assignment(user)

    # Handle no session
    if not next_session:
        return error_render("No assigned sessions found",
                            "No rota sessions assigned to your user were found")

    # Handle no current session
    if not session_is_current:
        return error_render("No current assigned session found",
                            "No rota session assigned to your user that is current was found")

    # Get most recent sign in for this session
    data = signed_in_out_session(user, next_session)

    # If not attendance found or last sign in not today
    if not data[1]:
        return error_render("Not signed in for assigned session",
                            "No sign in was found for the current assigned session")

    # If already signed out
    if data[2]:
        return error_render("Already signed out for assigned session",
                            "Your user has already signed out for the current assigned session")

    # Update attendance
    session = db_session()
    Attendance.query.with_session(session).filter_by(id=data[0].id).first().out_time = datetime.now()
    session.commit()

    return redirect(url_for("index"))
