from flask import render_template, redirect, url_for, flash, request
from app.blueprints.routes import routes_bp
from app.blueprints.routes.forms import RouteForm
from app.models import Route, Schedule, db
from sqlalchemy.exc import IntegrityError

@routes_bp.route('/')
def list_routes():
    """List all routes"""
    routes = Route.query.all()
    return render_template('routes/list.html', routes=routes)

@routes_bp.route('/add', methods=['GET', 'POST'])
def add_route():
    """Add a new route"""
    form = RouteForm()
    if form.validate_on_submit():
        try:
            route = Route(
                route_name=form.route_name.data,
                start_point=form.start_point.data,
                end_point=form.end_point.data,
                distance=form.distance.data,
                stops=form.stops.data
            )
            db.session.add(route)
            db.session.commit()
            flash(f'Route {route.route_name} added successfully!', 'success')
            return redirect(url_for('routes.list_routes'))
        except IntegrityError:
            db.session.rollback()
            flash('Route name already exists.', 'danger')
    return render_template('routes/form.html', form=form, title='Add New Route')

@routes_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_route(id):
    """Edit an existing route"""
    route = Route.query.get_or_404(id)
    form = RouteForm(obj=route)
    form.route_id = id

    if form.validate_on_submit():
        # Check route name uniqueness (excluding current route)
        existing = Route.query.filter_by(route_name=form.route_name.data).first()
        if existing and existing.id != id:
            flash('Route name already exists.', 'danger')
            return render_template('routes/form.html', form=form, title='Edit Route')

        route.route_name = form.route_name.data
        route.start_point = form.start_point.data
        route.end_point = form.end_point.data
        route.distance = form.distance.data
        route.stops = form.stops.data

        db.session.commit()
        flash(f'Route {route.route_name} updated successfully!', 'success')
        return redirect(url_for('routes.list_routes'))

    return render_template('routes/form.html', form=form, title='Edit Route')

@routes_bp.route('/delete/<int:id>', methods=['POST'])
def delete_route(id):
    """Delete a route"""
    route = Route.query.get_or_404(id)

    # Check if route is assigned to any schedules
    schedule_count = Schedule.query.filter_by(route_id=id).count()
    if schedule_count > 0:
        flash(f'Cannot delete route {route.route_name}. It is assigned to {schedule_count} schedule(s).', 'danger')
        return redirect(url_for('routes.list_routes'))

    db.session.delete(route)
    db.session.commit()
    flash(f'Route {route.route_name} deleted successfully!', 'success')
    return redirect(url_for('routes.list_routes'))
