from flask import render_template
from app.blueprints.dashboard import dashboard_bp
from app.models import Bus, Route, Schedule, Crew, db
from sqlalchemy import func
import json

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
