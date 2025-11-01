from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import db, Route, Schedule

route_bp = Blueprint('route', __name__, url_prefix='/route')

@route_bp.route('/list')
def list_routes():
    """Display all routes"""
    routes = Route.query.all()
    return render_template('routes.html', routes=routes)

@route_bp.route('/create', methods=['POST'])
def create_route():
    """Create a new route"""
    route_name = request.form.get('route_name', '').strip()
    start_location = request.form.get('start_location', '').strip()
    end_location = request.form.get('end_location', '').strip()
    distance = request.form.get('distance', '').strip()

    # Validate route_name
    if not route_name:
        flash('Route name is required', 'danger')
        return redirect(url_for('route.list_routes'))

    if len(route_name) > 100:
        flash('Route name must be 100 characters or less', 'danger')
        return redirect(url_for('route.list_routes'))

    # Validate start_location
    if not start_location:
        flash('Start location is required', 'danger')
        return redirect(url_for('route.list_routes'))

    if len(start_location) > 100:
        flash('Start location must be 100 characters or less', 'danger')
        return redirect(url_for('route.list_routes'))

    # Validate end_location
    if not end_location:
        flash('End location is required', 'danger')
        return redirect(url_for('route.list_routes'))

    if len(end_location) > 100:
        flash('End location must be 100 characters or less', 'danger')
        return redirect(url_for('route.list_routes'))

    # Validate distance
    if not distance:
        flash('Distance is required', 'danger')
        return redirect(url_for('route.list_routes'))

    try:
        distance_float = float(distance)
        if distance_float <= 0:
            flash('Distance must be greater than 0', 'danger')
            return redirect(url_for('route.list_routes'))
        if distance_float > 9999.99:
            flash('Distance cannot exceed 9999.99 km', 'danger')
            return redirect(url_for('route.list_routes'))
    except ValueError:
        flash('Distance must be a valid number', 'danger')
        return redirect(url_for('route.list_routes'))

    # Create route
    try:
        new_route = Route(
            route_name=route_name,
            start_location=start_location,
            end_location=end_location,
            distance=distance_float
        )
        db.session.add(new_route)
        db.session.commit()
        flash('Route created successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Database error occurred', 'danger')

    return redirect(url_for('route.list_routes'))

@route_bp.route('/update/<int:id>', methods=['POST'])
def update_route(id):
    """Update an existing route"""
    route = Route.query.get(id)
    if not route:
        flash('Route not found', 'danger')
        return redirect(url_for('route.list_routes'))

    route_name = request.form.get('route_name', '').strip()
    start_location = request.form.get('start_location', '').strip()
    end_location = request.form.get('end_location', '').strip()
    distance = request.form.get('distance', '').strip()

    # Validate route_name
    if not route_name:
        flash('Route name is required', 'danger')
        return redirect(url_for('route.list_routes'))

    if len(route_name) > 100:
        flash('Route name must be 100 characters or less', 'danger')
        return redirect(url_for('route.list_routes'))

    # Validate start_location
    if not start_location:
        flash('Start location is required', 'danger')
        return redirect(url_for('route.list_routes'))

    if len(start_location) > 100:
        flash('Start location must be 100 characters or less', 'danger')
        return redirect(url_for('route.list_routes'))

    # Validate end_location
    if not end_location:
        flash('End location is required', 'danger')
        return redirect(url_for('route.list_routes'))

    if len(end_location) > 100:
        flash('End location must be 100 characters or less', 'danger')
        return redirect(url_for('route.list_routes'))

    # Validate distance
    if not distance:
        flash('Distance is required', 'danger')
        return redirect(url_for('route.list_routes'))

    try:
        distance_float = float(distance)
        if distance_float <= 0:
            flash('Distance must be greater than 0', 'danger')
            return redirect(url_for('route.list_routes'))
        if distance_float > 9999.99:
            flash('Distance cannot exceed 9999.99 km', 'danger')
            return redirect(url_for('route.list_routes'))
    except ValueError:
        flash('Distance must be a valid number', 'danger')
        return redirect(url_for('route.list_routes'))

    # Update route
    try:
        route.route_name = route_name
        route.start_location = start_location
        route.end_location = end_location
        route.distance = distance_float
        db.session.commit()
        flash('Route updated successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Database error occurred', 'danger')

    return redirect(url_for('route.list_routes'))

@route_bp.route('/delete/<int:id>', methods=['POST'])
def delete_route(id):
    """Delete a route with undo capability"""
    route = Route.query.get(id)
    if not route:
        flash('Route not found', 'danger')
        return redirect(url_for('route.list_routes'))

    # Check if route is used in any schedules
    existing_schedule = Schedule.query.filter_by(route_id=id).first()
    if existing_schedule:
        flash('Cannot delete route with existing schedules', 'danger')
        return redirect(url_for('route.list_routes'))

    # Store route data in session for undo
    session['last_deleted_route'] = {
        'id': route.id,
        'route_name': route.route_name,
        'start_location': route.start_location,
        'end_location': route.end_location,
        'distance': route.distance
    }

    try:
        db.session.delete(route)
        db.session.commit()
        flash('Route deleted successfully. <a href="/route/undo" class="btn btn-sm btn-warning">Undo</a>', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Database error occurred', 'danger')

    return redirect(url_for('route.list_routes'))

@route_bp.route('/undo')
def undo_delete():
    """Restore last deleted route"""
    if 'last_deleted_route' not in session:
        flash('Nothing to undo', 'danger')
        return redirect(url_for('route.list_routes'))

    deleted_data = session.pop('last_deleted_route')

    try:
        # Re-insert with original ID
        new_route = Route(
            id=deleted_data['id'],
            route_name=deleted_data['route_name'],
            start_location=deleted_data['start_location'],
            end_location=deleted_data['end_location'],
            distance=deleted_data['distance']
        )
        db.session.add(new_route)
        db.session.commit()
        flash('Route restored successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Database error occurred', 'danger')

    return redirect(url_for('route.list_routes'))
