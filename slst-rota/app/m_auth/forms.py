from flask.ext.wtf import Form  # Form
from wtforms import StringField, PasswordField  # Form: Elements
from wtforms.validators import DataRequired  # Form: Validation


# Login (using WTForms)
class LoginForm(Form):
    username = StringField('Username', [DataRequired(message='Please enter your username.')])
    password = PasswordField('Password', [DataRequired(message='Please enter your password.')])
