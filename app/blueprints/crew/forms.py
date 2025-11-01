from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, DateField, TextAreaField
from wtforms.validators import DataRequired, ValidationError
from app.models import Crew, db

class CrewForm(FlaskForm):
    """Form for adding/editing crew members"""
    crew_id = StringField('Crew ID', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired()])
    role = SelectField('Role', choices=[
        ('Driver', 'Driver'),
        ('Conductor', 'Conductor'),
        ('Maintenance Staff', 'Maintenance Staff')
    ], validators=[DataRequired()])
    contact_info = StringField('Contact Info', validators=[DataRequired()])
    hire_date = DateField('Hire Date', format='%Y-%m-%d')

    def validate_crew_id(self, field):
        """Check if crew ID is unique"""
        if not hasattr(self, 'crew_db_id') or self.crew_db_id is None:
            crew = Crew.query.filter_by(crew_id=field.data).first()
            if crew:
                raise ValidationError('Crew ID already exists.')

class CrewAssignmentForm(FlaskForm):
    """Form for assigning crew to schedules"""
    schedule_id = SelectField('Schedule', coerce=int, validators=[DataRequired()])
    crew_id = SelectField('Crew Member', coerce=int, validators=[DataRequired()])
    assignment_date = DateField('Assignment Date', validators=[DataRequired()], format='%Y-%m-%d')
    notes = TextAreaField('Notes')
