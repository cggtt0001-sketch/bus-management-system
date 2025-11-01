from flask_wtf import FlaskForm
from wtforms import SelectField, TimeField, BooleanField
from wtforms.validators import DataRequired, ValidationError
from datetime import datetime

class ScheduleForm(FlaskForm):
    """Form for adding/editing schedules"""
    route_id = SelectField('Route', coerce=int, validators=[DataRequired()])
    bus_id = SelectField('Bus', coerce=int, validators=[DataRequired()])
    departure_time = TimeField('Departure Time', validators=[DataRequired()])
    arrival_time = TimeField('Arrival Time', validators=[DataRequired()])
    frequency = SelectField('Frequency', choices=[
        ('daily', 'Daily'),
        ('weekday', 'Weekday'),
        ('weekend', 'Weekend'),
        ('custom', 'Custom')
    ], validators=[DataRequired()])
    active = BooleanField('Active', default=True)

    def validate_arrival_time(self, field):
        """Validate that arrival time is after departure time"""
        if self.departure_time.data and field.data:
            if field.data <= self.departure_time.data:
                raise ValidationError('Arrival time must be after departure time.')
