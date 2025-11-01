from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Bus(db.Model):
    """Bus model for fleet management"""
    __tablename__ = 'buses'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    registration_number = db.Column(db.String(50), unique=True, nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    model = db.Column(db.String(100), nullable=True)
    status = db.Column(db.String(20), nullable=False, default='active')  # active, inactive, maintenance
    purchase_date = db.Column(db.Date, nullable=True)

    # Relationships
    schedules = db.relationship('Schedule', backref='bus', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Bus {self.registration_number}>'


class Route(db.Model):
    """Route model for defining bus routes"""
    __tablename__ = 'routes'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    route_name = db.Column(db.String(100), unique=True, nullable=False)
    start_point = db.Column(db.String(100), nullable=False)
    end_point = db.Column(db.String(100), nullable=False)
    distance = db.Column(db.Float, nullable=False)  # in km
    stops = db.Column(db.Text, nullable=True)  # comma-separated or JSON

    # Relationships
    schedules = db.relationship('Schedule', backref='route', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Route {self.route_name}>'


class Schedule(db.Model):
    """Schedule model for bus timetables"""
    __tablename__ = 'schedules'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    route_id = db.Column(db.Integer, db.ForeignKey('routes.id'), nullable=False)
    bus_id = db.Column(db.Integer, db.ForeignKey('buses.id'), nullable=False)
    departure_time = db.Column(db.Time, nullable=False)
    arrival_time = db.Column(db.Time, nullable=False)
    frequency = db.Column(db.String(20), nullable=False)  # daily, weekday, weekend, custom
    active = db.Column(db.Boolean, default=True, nullable=False)

    # Relationships
    crew_assignments = db.relationship('CrewAssignment', backref='schedule', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Schedule {self.route.route_name if self.route else "Unknown"} - {self.departure_time}>'


class Crew(db.Model):
    """Crew model for managing staff (drivers, conductors, maintenance)"""
    __tablename__ = 'crew'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    crew_id = db.Column(db.String(20), unique=True, nullable=False)  # e.g., DRV001, COND002
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(30), nullable=False)  # Driver, Conductor, Maintenance Staff
    contact_info = db.Column(db.String(100), nullable=False)  # phone/email
    hire_date = db.Column(db.Date, nullable=True)

    # Relationships
    assignments = db.relationship('CrewAssignment', backref='crew_member', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Crew {self.crew_id} - {self.name}>'


class CrewAssignment(db.Model):
    """Junction table for assigning crew to schedules"""
    __tablename__ = 'crew_assignments'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    schedule_id = db.Column(db.Integer, db.ForeignKey('schedules.id'), nullable=False)
    crew_id = db.Column(db.Integer, db.ForeignKey('crew.id'), nullable=False)
    assignment_date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    notes = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f'<CrewAssignment Crew:{self.crew_id} Schedule:{self.schedule_id}>'
