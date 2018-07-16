# Import Form
from flask.ext.wtf import Form

# Form elements
from wtforms import StringField, PasswordField  # BooleanField

# Form validators
from wtforms.validators import DataRequired


# Define the login form (using WTForms)
class LoginForm(Form):
    username = StringField('Username', [DataRequired(message='Please enter your username.')])
    password = PasswordField('Password', [DataRequired(message='Please enter your password.')])
