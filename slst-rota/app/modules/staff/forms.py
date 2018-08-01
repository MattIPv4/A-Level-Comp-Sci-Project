from flask_wtf import FlaskForm  # Form
from wtforms import StringField, PasswordField, SelectField  # Form: Elements
from wtforms.validators import DataRequired  # Form: Validation


# Account (using WTForms)
class AccountForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(message='Please enter a username.')])
    password = PasswordField('Password', validators=[DataRequired(message='Please enter a password.')])
    auth_level = SelectField('Auth Level', choices=[(1, "Student"), (2, "Staff")], coerce=int,
                             validators=[DataRequired(message='Please select an auth level.')])
