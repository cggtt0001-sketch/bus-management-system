from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Bus(db.Model):
    """Bus model for storing bus information"""
    __tablename__ = 'buses'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    bus_number = db.Column(db.Text, unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship to schedules
    schedules = db.relationship('Schedule', back_populates='bus', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Bus {self.bus_number}>'


class Route(db.Model):
    """Route model for storing route information"""
    __tablename__ = 'routes'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    route_name = db.Column(db.Text, nullable=False)
    start_location = db.Column(db.Text, nullable=False)
    end_location = db.Column(db.Text, nullable=False)
    distance = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship to schedules
    schedules = db.relationship('Schedule', back_populates='route', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Route {self.route_name}>'


class Schedule(db.Model):
    """Schedule model for storing bus schedule information"""
    __tablename__ = 'schedules'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    bus_id = db.Column(db.Integer, db.ForeignKey('buses.id', ondelete='CASCADE'), nullable=False)
    route_id = db.Column(db.Integer, db.ForeignKey('routes.id', ondelete='CASCADE'), nullable=False)
    departure_time = db.Column(db.Text, nullable=False)
    arrival_time = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    bus = db.relationship('Bus', back_populates='schedules')
    route = db.relationship('Route', back_populates='schedules')

    def __repr__(self):
        return f'<Schedule Bus:{self.bus_id} Route:{self.route_id} {self.departure_time}-{self.arrival_time}>'
