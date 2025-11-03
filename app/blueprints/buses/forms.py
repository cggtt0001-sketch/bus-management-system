from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, DateField, SubmitField
from wtforms.validators import DataRequired, NumberRange, ValidationError, Optional
from app.models import Bus, Route, Crew, db

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

    # New assignment fields
    route_id = SelectField('Assign Route', coerce=int, validators=[Optional()])
    driver_id = SelectField('Assign Driver', coerce=int, validators=[Optional()])
    conductor_id = SelectField('Assign Conductor', coerce=int, validators=[Optional()])

    submit = SubmitField('Save Bus')

    def __init__(self, *args, **kwargs):
        super(BusForm, self).__init__(*args, **kwargs)

        # Populate route choices
        self.route_id.choices = [(0, 'Select a route')] + [(r.id, r.route_name) for r in Route.query.all()]

        # Populate driver choices
        drivers = Crew.query.filter_by(role='Driver').all()
        self.driver_id.choices = [(0, 'Select a driver')] + [(d.id, f"{d.name} ({d.crew_id})") for d in drivers]

        # Populate conductor choices
        conductors = Crew.query.filter_by(role='Conductor').all()
        self.conductor_id.choices = [(0, 'Select a conductor')] + [(c.id, f"{c.name} ({c.crew_id})") for c in conductors]

    def validate_registration_number(self, field):
        """Check if registration number is unique"""
        # Only check if this is a new bus (no id attribute) or if registration changed
        if not hasattr(self, 'bus_id') or self.bus_id is None:
            bus = Bus.query.filter_by(registration_number=field.data).first()
            if bus:
                raise ValidationError('Registration number already exists.')
