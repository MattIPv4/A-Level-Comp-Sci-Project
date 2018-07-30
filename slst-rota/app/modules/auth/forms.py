from flask_wtf import FlaskForm  # Form
from wtforms import StringField, PasswordField, SelectField  # Form: Elements
from wtforms.validators import DataRequired  # Form: Validation


# Login (using WTForms)
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(message='Please enter your username.')])
    password = PasswordField('Password', validators=[DataRequired(message='Please enter your password.')])


# Account (using WTForms)
class AccountForm(FlaskForm):
    username = StringField('Username')
    auth_level = SelectField('Auth Level', choices=[(1, "Student"), (2, "Staff")], coerce=int)
    old_password = PasswordField('Old Password')
    new_password = PasswordField('New Password')
    new_password_confirm = PasswordField('New Password Confirmation')
