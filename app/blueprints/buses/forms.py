from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, DateField
from wtforms.validators import DataRequired, NumberRange, ValidationError
from app.models import Bus, db

class BusForm(FlaskForm):
    """Form for adding/editing buses"""
    registration_number = StringField('Registration Number', validators=[DataRequired()])
    capacity = IntegerField('Capacity', validators=[DataRequired(), NumberRange(min=1, message='Capacity must be at least 1')])
    model = StringField('Model')
    status = SelectField('Status', choices=[
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('maintenance', 'Maintenance')
    ], validators=[DataRequired()])
    purchase_date = DateField('Purchase Date', format='%Y-%m-%d')

    def validate_registration_number(self, field):
        """Check if registration number is unique"""
        # Only check if this is a new bus (no id attribute) or if registration changed
        if not hasattr(self, 'bus_id') or self.bus_id is None:
            bus = Bus.query.filter_by(registration_number=field.data).first()
            if bus:
                raise ValidationError('Registration number already exists.')
