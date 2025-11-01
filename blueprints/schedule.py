from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import db, Bus, Route, Schedule
import re

schedule_bp = Blueprint('schedule', __name__, url_prefix='/schedule')

def validate_time_format(time_str):
    """Validate time format HH:MM (24-hour)"""
    pattern = r'^([0-1][0-9]|2[0-3]):[0-5][0-9]$'
    return re.match(pattern, time_str) is not None

@schedule_bp.route('/list')
def list_schedules():
    """Display all schedules"""
    schedules = Schedule.query.join(Bus).join(Route).all()
    buses = Bus.query.all()
    routes = Route.query.all()
    return render_template('schedules.html', schedules=schedules, buses=buses, routes=routes)

@schedule_bp.route('/create', methods=['POST'])
def create_schedule():
    """Create a new schedule"""
    bus_id = request.form.get('bus_id', '').strip()
    route_id = request.form.get('route_id', '').strip()
    departure_time = request.form.get('departure_time', '').strip()
    arrival_time = request.form.get('arrival_time', '').strip()

    # Validate bus_id
    if not bus_id:
        flash('Bus is required', 'danger')
        return redirect(url_for('schedule.list_schedules'))

    try:
        bus_id = int(bus_id)
        bus = Bus.query.get(bus_id)
        if not bus:
            flash('Selected bus does not exist', 'danger')
            return redirect(url_for('schedule.list_schedules'))
    except ValueError:
        flash('Bus is required', 'danger')
        return redirect(url_for('schedule.list_schedules'))

    # Validate route_id
    if not route_id:
        flash('Route is required', 'danger')
        return redirect(url_for('schedule.list_schedules'))

    try:
        route_id = int(route_id)
        route = Route.query.get(route_id)
        if not route:
            flash('Selected route does not exist', 'danger')
            return redirect(url_for('schedule.list_schedules'))
    except ValueError:
        flash('Route is required', 'danger')
        return redirect(url_for('schedule.list_schedules'))

    # Validate departure_time
    if not departure_time:
        flash('Departure time is required', 'danger')
        return redirect(url_for('schedule.list_schedules'))

    if not validate_time_format(departure_time):
        flash('Departure time must be in HH:MM format (e.g., 08:30)', 'danger')
        return redirect(url_for('schedule.list_schedules'))

    # Validate arrival_time
    if not arrival_time:
        flash('Arrival time is required', 'danger')
        return redirect(url_for('schedule.list_schedules'))

    if not validate_time_format(arrival_time):
        flash('Arrival time must be in HH:MM format (e.g., 10:30)', 'danger')
        return redirect(url_for('schedule.list_schedules'))

    # Create schedule
    try:
        new_schedule = Schedule(
            bus_id=bus_id,
            route_id=route_id,
            departure_time=departure_time,
            arrival_time=arrival_time
        )
        db.session.add(new_schedule)
        db.session.commit()
        flash('Schedule created successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Database error occurred', 'danger')

    return redirect(url_for('schedule.list_schedules'))

@schedule_bp.route('/update/<int:id>', methods=['POST'])
def update_schedule(id):
    """Update an existing schedule"""
    schedule = Schedule.query.get(id)
    if not schedule:
        flash('Schedule not found', 'danger')
        return redirect(url_for('schedule.list_schedules'))

    bus_id = request.form.get('bus_id', '').strip()
    route_id = request.form.get('route_id', '').strip()
    departure_time = request.form.get('departure_time', '').strip()
    arrival_time = request.form.get('arrival_time', '').strip()

    # Validate bus_id
    if not bus_id:
        flash('Bus is required', 'danger')
        return redirect(url_for('schedule.list_schedules'))

    try:
        bus_id = int(bus_id)
        bus = Bus.query.get(bus_id)
        if not bus:
            flash('Selected bus does not exist', 'danger')
            return redirect(url_for('schedule.list_schedules'))
    except ValueError:
        flash('Bus is required', 'danger')
        return redirect(url_for('schedule.list_schedules'))

    # Validate route_id
    if not route_id:
        flash('Route is required', 'danger')
        return redirect(url_for('schedule.list_schedules'))

    try:
        route_id = int(route_id)
        route = Route.query.get(route_id)
        if not route:
            flash('Selected route does not exist', 'danger')
            return redirect(url_for('schedule.list_schedules'))
    except ValueError:
        flash('Route is required', 'danger')
        return redirect(url_for('schedule.list_schedules'))

    # Validate departure_time
    if not departure_time:
        flash('Departure time is required', 'danger')
        return redirect(url_for('schedule.list_schedules'))

    if not validate_time_format(departure_time):
        flash('Departure time must be in HH:MM format (e.g., 08:30)', 'danger')
        return redirect(url_for('schedule.list_schedules'))

    # Validate arrival_time
    if not arrival_time:
        flash('Arrival time is required', 'danger')
        return redirect(url_for('schedule.list_schedules'))

    if not validate_time_format(arrival_time):
        flash('Arrival time must be in HH:MM format (e.g., 10:30)', 'danger')
        return redirect(url_for('schedule.list_schedules'))

    # Update schedule
    try:
        schedule.bus_id = bus_id
        schedule.route_id = route_id
        schedule.departure_time = departure_time
        schedule.arrival_time = arrival_time
        db.session.commit()
        flash('Schedule updated successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Database error occurred', 'danger')

    return redirect(url_for('schedule.list_schedules'))

@schedule_bp.route('/delete/<int:id>', methods=['POST'])
def delete_schedule(id):
    """Delete a schedule with undo capability"""
    schedule = Schedule.query.get(id)
    if not schedule:
        flash('Schedule not found', 'danger')
        return redirect(url_for('schedule.list_schedules'))

    # Store schedule data in session for undo
    session['last_deleted_schedule'] = {
        'id': schedule.id,
        'bus_id': schedule.bus_id,
        'route_id': schedule.route_id,
        'departure_time': schedule.departure_time,
        'arrival_time': schedule.arrival_time
    }

    try:
        db.session.delete(schedule)
        db.session.commit()
        flash('Schedule deleted successfully. <a href="/schedule/undo" class="btn btn-sm btn-warning">Undo</a>', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Database error occurred', 'danger')

    return redirect(url_for('schedule.list_schedules'))

@schedule_bp.route('/undo')
def undo_delete():
    """Restore last deleted schedule"""
    if 'last_deleted_schedule' not in session:
        flash('Nothing to undo', 'danger')
        return redirect(url_for('schedule.list_schedules'))

    deleted_data = session.pop('last_deleted_schedule')

    try:
        # Re-insert with original ID
        new_schedule = Schedule(
            id=deleted_data['id'],
            bus_id=deleted_data['bus_id'],
            route_id=deleted_data['route_id'],
            departure_time=deleted_data['departure_time'],
            arrival_time=deleted_data['arrival_time']
        )
        db.session.add(new_schedule)
        db.session.commit()
        flash('Schedule restored successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Database error occurred', 'danger')

    return redirect(url_for('schedule.list_schedules'))
