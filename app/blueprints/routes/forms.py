from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, TextAreaField
from wtforms.validators import DataRequired, NumberRange, ValidationError
from app.models import Route, db

class RouteForm(FlaskForm):
    """Form for adding/editing routes"""
    route_name = StringField('Route Name', validators=[DataRequired()])
    start_point = StringField('Start Point', validators=[DataRequired()])
    end_point = StringField('End Point', validators=[DataRequired()])
    distance = FloatField('Distance (km)', validators=[DataRequired(), NumberRange(min=0.1, message='Distance must be at least 0.1 km')])
    stops = TextAreaField('Stops')

    def validate_route_name(self, field):
        """Check if route name is unique"""
        if not hasattr(self, 'route_id') or self.route_id is None:
            route = Route.query.filter_by(route_name=field.data).first()
            if route:
                raise ValidationError('Route name already exists.')
