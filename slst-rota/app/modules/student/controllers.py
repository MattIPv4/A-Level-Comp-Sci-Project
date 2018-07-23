from flask import Blueprint, request, render_template, flash, session, redirect, url_for  # Flask

from app import db_session, error_render  # DB, Errors
from app.modules import auth # Auth
from app.modules.student.models import Session # Rota Sessions

# Blueprint
student = Blueprint('student', __name__, url_prefix='/student')


# Rota
@student.route('/', methods=['GET'])
def rota():
    user = auth.current_user()

    # If no session exists
    if not user:
        return redirect(url_for('auth.login'))

    # If not student
    if user.auth_level != 1:
        return error_render("Student access only",
                            "This page is only accessible to users with the student authentication level")

    return render_template("student/rota.jinja2", title="Rota view for {}".format(user.username))

# Full Rota
@student.route('/full/', methods=['GET'])
def rota_full():
    user = auth.current_user()

    # If no session exists
    if not user:
        return redirect(url_for('auth.login'))

    # If not student
    if user.auth_level != 1:
        return error_render("Student access only",
                            "This page is only accessible to users with the student authentication level")

    return render_template("student/rota.jinja2", title="Full rota view")
