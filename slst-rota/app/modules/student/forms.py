from flask_wtf import FlaskForm # Form
from wtforms import StringField, BooleanField  # Form: Elements


# Unavailability (using WTForms)
class UnavailabilityForm(FlaskForm):
    unavailable = BooleanField('Unavailable')
    reason = StringField('Reason')