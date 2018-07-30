from flask_wtf import FlaskForm  # Form
from wtforms import StringField, BooleanField, PasswordField  # Form: Elements
from wtforms.validators import DataRequired  # Form: Validation


# Unavailability (using WTForms)
class UnavailabilityForm(FlaskForm):
    unavailable = BooleanField('Unavailable')
    reason = StringField('Reason')


# Account (using WTForms)
class AccountForm(FlaskForm):
    old_password = PasswordField('Old Password',
                                 validators=[DataRequired(message='Please enter your old password.')])
    new_password = PasswordField('New Password',
                                 validators=[DataRequired(message='Please enter your new password.')])
    new_password_confirm = PasswordField('New Password Confirmation',
                                         validators=[DataRequired(message='Please enter your new password.')])
