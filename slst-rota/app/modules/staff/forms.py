from flask_wtf import FlaskForm  # Form
from wtforms import StringField, PasswordField, SelectField, TimeField # Form: Elements
from wtforms.validators import DataRequired  # Form: Validation
import calendar # Calendar


# Account (using WTForms)
class AccountForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(message='Please enter a username.')])
    password = PasswordField('Password', validators=[DataRequired(message='Please enter a password.')])
    auth_level = SelectField('Auth Level', choices=[(1, "Student"), (2, "Staff")], coerce=int,
                             validators=[DataRequired(message='Please select an auth level.')])


# Session (using WTForms)
class SessionForm(FlaskForm):
    day = SelectField('Day of Week', choices=[(f, calendar.day_name[f]) for f in range(len(calendar.day_name))],
                      coerce=int, validators=[DataRequired(message='Please select a day of the week.')])
    start_time = TimeField('Start Time', validators=[DataRequired(message='Please enter a start time.')])
    end_time = TimeField('End Time', validators=[DataRequired(message='Please enter an end time.')])