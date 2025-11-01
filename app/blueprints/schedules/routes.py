from flask import render_template, redirect, url_for, flash, request
from app.blueprints.schedules import schedules_bp
from app.blueprints.schedules.forms import ScheduleForm
from app.models import Schedule, Route, Bus, db
from sqlalchemy.exc import IntegrityError

@schedules_bp.route('/')
def list_schedules():
    """List all schedules"""
    schedules = Schedule.query.all()
    return render_template('schedules/list.html', schedules=schedules)

@schedules_bp.route('/add', methods=['GET', 'POST'])
def add_schedule():
    """Add a new schedule"""
    form = ScheduleForm()

    # Populate route and bus choices
    routes = Route.query.all()
    buses = Bus.query.all()

    if not routes or not buses:
        flash('Please add routes and buses before creating schedules.', 'warning')
        return render_template('schedules/form.html', form=form, title='Add New Schedule', no_data=True)

    form.route_id.choices = [(r.id, r.route_name) for r in routes]
    form.bus_id.choices = [(b.id, b.registration_number) for b in buses]

    if form.validate_on_submit():
        # Check for bus scheduling conflict
        existing_schedules = Schedule.query.filter_by(
            bus_id=form.bus_id.data,
            departure_time=form.departure_time.data
        ).all()

        if existing_schedules:
            bus = Bus.query.get(form.bus_id.data)
            flash(f'Bus {bus.registration_number} is already scheduled at this time.', 'danger')
            return render_template('schedules/form.html', form=form, title='Add New Schedule')

        schedule = Schedule(
            route_id=form.route_id.data,
            bus_id=form.bus_id.data,
            departure_time=form.departure_time.data,
            arrival_time=form.arrival_time.data,
            frequency=form.frequency.data,
            active=form.active.data
        )
        db.session.add(schedule)
        db.session.commit()
        flash('Schedule added successfully!', 'success')
        return redirect(url_for('schedules.list_schedules'))

    return render_template('schedules/form.html', form=form, title='Add New Schedule')

@schedules_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_schedule(id):
    """Edit an existing schedule"""
    schedule = Schedule.query.get_or_404(id)
    form = ScheduleForm(obj=schedule)

    # Populate route and bus choices
    routes = Route.query.all()
    buses = Bus.query.all()
    form.route_id.choices = [(r.id, r.route_name) for r in routes]
    form.bus_id.choices = [(b.id, b.registration_number) for b in buses]

    if form.validate_on_submit():
        # Check for bus scheduling conflict (excluding current schedule)
        existing_schedules = Schedule.query.filter(
            Schedule.bus_id == form.bus_id.data,
            Schedule.departure_time == form.departure_time.data,
            Schedule.id != id
        ).all()

        if existing_schedules:
            bus = Bus.query.get(form.bus_id.data)
            flash(f'Bus {bus.registration_number} is already scheduled at this time.', 'danger')
            return render_template('schedules/form.html', form=form, title='Edit Schedule')

        schedule.route_id = form.route_id.data
        schedule.bus_id = form.bus_id.data
        schedule.departure_time = form.departure_time.data
        schedule.arrival_time = form.arrival_time.data
        schedule.frequency = form.frequency.data
        schedule.active = form.active.data

        db.session.commit()
        flash('Schedule updated successfully!', 'success')
        return redirect(url_for('schedules.list_schedules'))

    return render_template('schedules/form.html', form=form, title='Edit Schedule')

@schedules_bp.route('/delete/<int:id>', methods=['POST'])
def delete_schedule(id):
    """Delete a schedule"""
    schedule = Schedule.query.get_or_404(id)

    # Crew assignments will be cascaded automatically
    db.session.delete(schedule)
    db.session.commit()
    flash('Schedule deleted successfully!', 'success')
    return redirect(url_for('schedules.list_schedules'))
