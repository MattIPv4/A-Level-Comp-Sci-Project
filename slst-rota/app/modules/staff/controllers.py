import calendar  # Calendar
import json  # JSON
from datetime import datetime  # Datetime
from typing import List, Union, Dict  # Typing

from flask import Blueprint, render_template, redirect, url_for, request, flash  # Flask
from werkzeug.security import generate_password_hash  # Passwords

from app import db_session, error_render, Utils  # DB, Errors, Utils
from app.modules import auth  # Auth
from app.modules.auth import User  # User
from app.modules.staff.forms import AccountForm, SessionForm, SessionDeleteForm, \
    AssignmentForm, AutomaticAssignmentForm  # Forms
from app.modules.student import Session, Assignment, Unavailability  # Session

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


# Fetch the next user in the rotation that is assignable
def next_assignable(total_assigned: Dict[int, list], assigned: List[User], session: Session,
                    force_next: bool = False) -> Union[None, User]:
    # The user that hopefully will be found
    next_user = None

    # Order users by assignments so far (smallest first)
    users_sorted = sorted(total_assigned.values(), key=lambda x: x[0])

    # Loop over users until we find one (least assignments first)
    for user in users_sorted:
        # Get the user object
        user_obj = user[1]  # [int (assignments), user]

        # Check if already assigned
        if user_obj in assigned:
            continue

        # Check if available
        unavailable = Unavailability.query.filter_by(session_id=session.id, user_id=user_obj.id).all()
        if unavailable:
            continue

        # Store
        next_user = user
        break

    # If all unavailable and want to force, select first
    if force_next and next_user is None:
        users_sorted = [f for f in users_sorted if f[1] not in assigned]
        if users_sorted:
            next_user = users_sorted[0]

    # If have user, update assinged
    if next_user is not None:
        next_user = next_user[1]
        assigned.append(next_user)
        total_assigned[next_user.id][0] += 1

    # Done
    return next_user


# Generate assignments
def generate_assignments(users_per_session: int = 1, force_user: bool = True):
    # Fetch all sessions
    sessions = Session.query.filter_by(archived=False).all()
    if not sessions:
        return

    # Fetch all users
    users = User.query.filter_by(auth_level=1, disabled=False).all()
    if not users:
        return

    # DB
    dbsession = db_session()

    # Remove old assignments
    assignments = Assignment.query.with_session(dbsession).filter_by(removed=None).all()
    for assignment in assignments:
        assignment.removed = datetime.now()
    dbsession.commit()

    # Loop over sessions
    total_assigned = {f.id: [0, f] for f in users}
    for session in sessions:
        # Correct number of users per session
        target = users_per_session
        assigned = []

        # Loop for target
        while target > 0:

            # Get next user to assign (will also update both assigned)
            student = next_assignable(total_assigned, assigned, session, force_user)

            # Give up if no users
            if not student:
                break

            # Update target
            target -= 1
            # Assign
            assignment = Assignment(student.id, session.id)
            dbsession.add(assignment)
            dbsession.commit()


# All accounts
@staff.route('/accounts/', methods=['GET'])
def accounts():
    user, error = auth_check()
    if error:
        return error

    data = User.query.all()
    all_accounts = []
    for item in data:
        all_accounts.append([
            item.id == user.id,
            [
                item.username,
                "{} ({})".format(item.auth_label, item.auth_level),
                "Yes" if item.disabled == 1 else "No",
                "<a href='{}' class='button'><i class=\"fas fa-lg fa-user-edit\"></i> Edit</a>".format(
                    url_for("auth.account", id=item.id))
            ]
        ])

    return render_template("staff/accounts.jinja2", accounts=all_accounts)


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
                        user = User(form.username.data, generate_password_hash(form.password.data),
                                    form.auth_level.data)
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
            ([f for f in session.assignments if not f.removed] == []),
            [
                session.start_time_frmt,
                session.end_time_frmt,
                ", ".join(
                    [f.user.username for f in session.assignments if not f.removed and not f.user.disabled]) or "None",
                "<a href='{}' class='button'><i class=\"fas fa-lg fa-edit\"></i> Edit Session</a>"
                "".format(url_for("staff.rota_edit_session", id=session.id)) +
                " &nbsp; <a href='{}' class='button'><i class=\"fas fa-lg fa-users-cog\"></i> Update Assignments</a>"
                "".format(url_for("staff.rota_edit_assignments", id=session.id))
            ]
        ])

    return render_template("staff/rota.jinja2", rota_data=rota_data)


# Rota edit - session
@staff.route('/rota/edit/session/<int:id>', methods=['GET', 'POST'])
def rota_edit_session(id: int):
    user, error = auth_check()
    if error:
        return error

    # Get session data
    session = Session.query.filter_by(archived=False, id=id).first()

    # If bad session
    if not session:
        return redirect(url_for('staff.rota'))

    # Form
    form = SessionForm(request.form)

    # Verify the form
    if form.validate_on_submit():

        # Verify day
        if form.day.data:

            # Verify start time
            if form.start_time.data:

                # Verify end time
                if form.end_time.data:

                    # Verify times
                    if form.start_time.data < form.end_time.data:

                        dbsession = db_session()
                        session = Session.query.with_session(dbsession).filter_by(id=id).first()

                        start_time = datetime.combine(datetime.now().date(), form.start_time.data)
                        start_time = int(Utils.minutes_datetime(start_time))

                        end_time = datetime.combine(datetime.now().date(), form.end_time.data)
                        end_time = int(Utils.minutes_datetime(end_time))

                        session.day = form.day.data
                        session.start_time = start_time
                        session.end_time = end_time

                        dbsession.commit()
                        return redirect(url_for('staff.rota'))

                    else:
                        flash('Start time must be before end time')

                else:
                    flash('Please enter an end time')

            else:
                flash('Please enter a start time')

        else:
            flash('Please select a day of the week')

    # Errors
    if form.errors:
        for field, error in form.errors.items():
            flash('{}: {}'.format(field, ", ".join(error)))

    # Values
    form.day.data = session.day
    form.start_time.data = session.start_time_time
    form.end_time.data = session.end_time_time

    # Render
    return render_template("staff/session_edit.jinja2", form=form, title_type="Edit", button_type="Update", id=id)


# Rota delete - session
@staff.route('/rota/edit/session/<int:id>/delete', methods=['GET', 'POST'])
def rota_delete_session(id: int):
    user, error = auth_check()
    if error:
        return error

    # Get session data
    session = Session.query.filter_by(archived=False, id=id).first()

    # If bad session
    if not session:
        return redirect(url_for('staff.rota'))

    # Form
    form = SessionDeleteForm(request.form)

    # Verify the form
    if form.validate_on_submit():
        # Get session
        dbsession = db_session()
        session = Session.query.with_session(dbsession).filter_by(id=id).first()

        # Remove old assignments
        assignments = Assignment.query.with_session(dbsession).filter_by(session_id=id, removed=None).all()
        for assignment in assignments:
            assignment.removed = datetime.now()
        dbsession.commit()

        # Remove session
        session.archived = 1

        # Save
        dbsession.commit()
        return redirect(url_for('staff.rota'))

    # Render
    return render_template("staff/session_delete.jinja2", form=form, id=id)


# New rota session
@staff.route('/rota/new', methods=['GET', 'POST'])
def rota_new():
    user, error = auth_check()
    if error:
        return error

    # Form
    form = SessionForm(request.form)

    # Verify the form
    if form.validate_on_submit():

        # Verify day
        if form.day.data is not None:

            # Verify start time
            if form.start_time.data is not None:

                # Verify end time
                if form.end_time.data is not None:

                    # Verify times
                    if form.start_time.data < form.end_time.data:

                        dbsession = db_session()

                        start_time = datetime.combine(datetime.now().date(), form.start_time.data)
                        start_time = int(Utils.minutes_datetime(start_time))

                        end_time = datetime.combine(datetime.now().date(), form.end_time.data)
                        end_time = int(Utils.minutes_datetime(end_time))

                        session = Session(form.day.data, start_time, end_time)
                        dbsession.add(session)

                        dbsession.commit()
                        return redirect(url_for('staff.rota'))

                    else:
                        flash('Start time must be before end time')

                else:
                    flash('Please enter an end time')

            else:
                flash('Please enter a start time')

        else:
            flash('Please select a day of the week')

    # Errors
    if form.errors:
        for field, error in form.errors.items():
            flash('{}: {}'.format(field, ", ".join(error)))

    # Render
    return render_template("staff/session_edit.jinja2", form=form, title_type="New", button_type="Create")


# Rota edit - assignments
@staff.route('/rota/edit/assignments/<int:id>', methods=['GET', 'POST'])
def rota_edit_assignments(id: int):
    user, error = auth_check()
    if error:
        return error

    # Get session data
    session = Session.query.filter_by(archived=False, id=id).first()

    # If bad session
    if not session:
        return redirect(url_for('staff.rota'))

    # Compile assignments
    assigned = [(f.user.id, f.user.username,
                 True if Unavailability.query.filter_by(session=session, user=f.user).all() else False) for f in
                session.assignments if not f.removed and not f.user.disabled]
    unassigned = [(f.id, f.username,
                   True if Unavailability.query.filter_by(session=session, user=f).all() else False)
                  for f in User.query.filter_by(auth_level=1).all() if f.id not in [g[0] for g in assigned] and
                  not f.disabled]

    # Fetch unavailabilities
    unavailable = [f for f in Unavailability.query.filter_by(session=session).all() if not f.user.disabled]

    # Form
    form = AssignmentForm(request.form)

    # Verify the form
    if form.validate_on_submit():
        try:
            form.assigned.data = json.loads(form.assigned.data)
        except:
            flash('An error occurred parsing the JSON data')
        else:
            to_remove = [f[0] for f in assigned if f[0] not in form.assigned.data]
            to_add = [f for f in form.assigned.data if f not in [g[0] for g in assigned]]

            dbsession = db_session()

            for remove in to_remove:
                assignment = Assignment.query.with_session(dbsession).filter_by(user_id=remove, session_id=session.id,
                                                                                removed=None).first()
                assignment.removed = datetime.now()
                dbsession.commit()

            for add in to_add:
                assignment = Assignment(add, session.id)
                dbsession.add(assignment)
                dbsession.commit()

            return redirect(url_for('staff.rota'))

    # Errors
    if form.errors:
        for field, error in form.errors.items():
            flash('{}: {}'.format(field, ", ".join(error)))

    # Values
    form.assigned.data = json.dumps([f[0] for f in assigned])

    # Render
    return render_template("staff/assignment_edit.jinja2", form=form,
                           assigned=assigned, unassigned=unassigned,
                           unavailable=unavailable)


# Rota edit - automatic assignments
@staff.route('/rota/auto', methods=['GET', 'POST'])
def rota_automatic_assignments():
    user, error = auth_check()
    if error:
        return error

    # Check sessions
    sessions = Session.query.filter_by(archived=False).all()
    if not sessions:
        return error_render(503, "No sessions are currently in the rota. Please define a session before automatically "
                                 "assigning students to the rota.")

    # Check students
    users = User.query.filter_by(auth_level=1, disabled=False).all()
    if not users:
        return error_render(503, "No students are in the system. Please create a user (not disabled) before attempting "
                                 "to assign them to rota sessions.")

    # Get form and set checks
    form = AutomaticAssignmentForm(request.form)
    form.count.widget.min = 1
    form.count.widget.max = len(users)

    # Verify the form
    if form.validate_on_submit():
        # Check count is in range
        if form.count.data and 1 <= form.count.data <= len(users):
            force = bool(form.force.data)  # Ensure bool
            try:
                generate_assignments(form.count.data, force)
            except:
                flash('An error occurred whilst generating the automatic assignments. Please try again.')
            else:
                flash('Assignments have been successfully generated. Press the Back button to view the rota.')
        else:
            flash('Students per session must be 1 or more and must be less then or equal to the total number of '
                  'students in the system ({:,})'.format(len(users)))

    # Errors
    if form.errors:
        for field, error in form.errors.items():
            flash('{}: {}'.format(field, ", ".join(error)))

    # Render
    return render_template("staff/automatic_assignments.jinja2", form=form)
