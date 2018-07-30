from flask import Blueprint, render_template, redirect, url_for  # Flask

from app import error_render  # Errors
from app.modules import auth  # Auth
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
