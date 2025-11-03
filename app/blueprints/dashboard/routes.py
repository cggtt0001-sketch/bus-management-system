from flask import render_template
from app.blueprints.dashboard import dashboard_bp
from app.models import Bus, Route, Schedule, Crew, CrewAssignment, db
from sqlalchemy import func
import json
import random
from datetime import datetime

@dashboard_bp.route('/')
def index():
    """Display analytics dashboard with charts and statistics"""

    # Summary statistics
    total_buses = Bus.query.count()
    total_routes = Route.query.count()
    total_schedules = Schedule.query.count()
    total_crew = Crew.query.count()

    # Bus status breakdown
    active_buses = Bus.query.filter_by(status='active').count()
    inactive_buses = Bus.query.filter(Bus.status != 'active').count()

    # Schedule frequency distribution
    frequency_data = db.session.query(
        Schedule.frequency,
        func.count(Schedule.id)
    ).group_by(Schedule.frequency).all()

    frequency_labels = [item[0].capitalize() for item in frequency_data]
    frequency_counts = [item[1] for item in frequency_data]

    # Route utilization (number of schedules per route)
    route_data = db.session.query(
        Route.route_name,
        func.count(Schedule.id)
    ).join(Schedule).group_by(Route.id, Route.route_name).all()

    route_labels = [item[0] for item in route_data]
    route_counts = [item[1] for item in route_data]

    # Convert to JSON for JavaScript
    frequency_data_json = json.dumps({
        'labels': frequency_labels,
        'data': frequency_counts
    })

    route_data_json = json.dumps({
        'labels': route_labels,
        'data': route_counts
    })

    return render_template(
        'dashboard/index.html',
        total_buses=total_buses,
        total_routes=total_routes,
        total_schedules=total_schedules,
        total_crew=total_crew,
        active_buses=active_buses,
        inactive_buses=inactive_buses,
        frequency_data=frequency_data_json,
        route_data=route_data_json
    )


def generate_mock_coordinates(bus_id, route_start_point, route_end_point):
    """Generate realistic mock GPS coordinates for a bus"""

    # City center coordinates (can be configured)
    city_lat = 40.7128  # NYC latitude
    city_lng = -74.0060  # NYC longitude

    # Generate coordinates within city bounds
    lat_offset = (random.random() - 0.5) * 0.1  # ±0.05 degrees
    lng_offset = (random.random() - 0.5) * 0.1  # ±0.05 degrees

    return {
        'lat': city_lat + lat_offset,
        'lng': city_lng + lng_offset,
        'timestamp': datetime.utcnow()
    }


@dashboard_bp.route('/map')
def map_dashboard():
    """Display live map of active buses"""

    # Get all active buses with their schedules and crew assignments
    active_buses = db.session.query(Bus, Schedule, Route, Crew).join(
        Schedule, Bus.id == Schedule.bus_id
    ).join(
        Route, Schedule.route_id == Route.id
    ).join(
        CrewAssignment, Schedule.id == CrewAssignment.schedule_id
    ).join(
        Crew, CrewAssignment.crew_id == Crew.id
    ).filter(
        Bus.status == 'active',
        Schedule.active == True
    ).all()

    # Format data for JavaScript
    bus_data = []
    for bus, schedule, route, crew in active_buses:
        # Generate mock GPS coordinates if not present
        if bus.location_lat is None or bus.location_lng is None:
            # Simple mock coordinates around city center (can be made more realistic)
            bus.location_lat = 40.7128 + (random.random() - 0.5) * 0.1  # NYC area mock
            bus.location_lng = -74.0060 + (random.random() - 0.5) * 0.1
            bus.last_location_update = datetime.utcnow()

        bus_data.append({
            'id': bus.id,
            'registration_number': bus.registration_number,
            'lat': bus.location_lat,
            'lng': bus.location_lng,
            'status': bus.status,
            'route_name': route.route_name,
            'start_point': route.start_point,
            'end_point': route.end_point,
            'driver_name': crew.name if crew.role == 'Driver' else 'Unassigned',
            'conductor_name': crew.name if crew.role == 'Conductor' else 'Unassigned',
            'last_update': bus.last_location_update.isoformat() if bus.last_location_update else None
        })

    return render_template('dashboard/map.html', bus_data=bus_data)
