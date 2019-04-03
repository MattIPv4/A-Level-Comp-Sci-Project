import calendar  # Calendar

from flask_wtf import FlaskForm  # Form
from wtforms import StringField, PasswordField, SelectField, TimeField, HiddenField, \
    IntegerField, BooleanField  # Form: Elements
from wtforms.validators import DataRequired  # Form: Validation
from wtforms.widgets.html5 import NumberInput  # Number input


# Account (using WTForms)
class AccountForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(message='Please enter a username.')])
    password = PasswordField('Password', validators=[DataRequired(message='Please enter a password.')])
    auth_level = SelectField('Auth Level', choices=[(1, "Student"), (2, "Staff")], coerce=int,
                             validators=[DataRequired(message='Please select an auth level.')])


# Session (using WTForms)
class SessionForm(FlaskForm):
    day = SelectField('Day of Week', choices=[(f, calendar.day_name[f]) for f in range(len(calendar.day_name))],
                      coerce=int, default=0)
    start_time = TimeField('Start Time', validators=[
        DataRequired(message='Please enter a start time and ensure it is in the correct format.')])
    end_time = TimeField('End Time', validators=[
        DataRequired(message='Please enter an end time and ensure it is in the correct format.')])


# Session Delete
class SessionDeleteForm(FlaskForm):
    pass


# Assignments
class AssignmentForm(FlaskForm):
    assigned = HiddenField()


# Automatic Assignments
class AutomaticAssignmentForm(FlaskForm):
    count = IntegerField('Students per Session', validators=[DataRequired(
        message='Please enter a number of students to assign per session')], widget=NumberInput(), default=1)
    force = BooleanField('Force students to be assigned')
