from flask import render_template, redirect, url_for, flash, request
from app.blueprints.buses import buses_bp
from app.blueprints.buses.forms import BusForm
from app.models import Bus, Route, Crew, Schedule, CrewAssignment, db
from sqlalchemy.exc import IntegrityError
from datetime import datetime

@buses_bp.route('/')
def list_buses():
    """List all buses"""
    buses = Bus.query.all()
    return render_template('buses/list.html', buses=buses)

@buses_bp.route('/create', methods=['GET', 'POST'])
def create_bus():
    """Create a new bus with optional route and crew assignment"""
    form = BusForm()

    if form.validate_on_submit():
        # Create bus
        bus = Bus(
            registration_number=form.registration_number.data,
            capacity=form.capacity.data,
            model=form.model.data,
            purchase_date=form.purchase_date.data,
            status='active'  # Automatically mark as active
        )

        db.session.add(bus)
        db.session.flush()  # Get bus ID without committing

        # If route and crew are assigned, create schedule and assignments
        if form.route_id.data and form.driver_id.data:
            # Create a default schedule
            schedule = Schedule(
                route_id=form.route_id.data,
                bus_id=bus.id,
                departure_time=datetime.now().time().replace(hour=8, minute=0),  # 8:00 AM default
                arrival_time=datetime.now().time().replace(hour=17, minute=0),  # 5:00 PM default
                frequency='daily',
                active=True
            )
            db.session.add(schedule)
            db.session.flush()  # Get schedule ID

            # Assign driver
            if form.driver_id.data:
                driver_assignment = CrewAssignment(
                    schedule_id=schedule.id,
                    crew_id=form.driver_id.data,
                    assignment_date=datetime.now().date()
                )
                db.session.add(driver_assignment)

            # Assign conductor if provided
            if form.conductor_id.data:
                conductor_assignment = CrewAssignment(
                    schedule_id=schedule.id,
                    crew_id=form.conductor_id.data,
                    assignment_date=datetime.now().date()
                )
                db.session.add(conductor_assignment)

        db.session.commit()
        flash(f'Bus {bus.registration_number} has been created successfully!', 'success')
        return redirect(url_for('buses.list_buses'))

    return render_template('buses/enhanced_form.html', form=form, title='Add New Bus')

@buses_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_bus(id):
    """Edit an existing bus"""
    bus = Bus.query.get_or_404(id)
    form = BusForm(obj=bus)
    form.bus_id = id  # Store ID for validation

    if form.validate_on_submit():
        # Check registration number uniqueness (excluding current bus)
        existing = Bus.query.filter_by(registration_number=form.registration_number.data).first()
        if existing and existing.id != id:
            flash('Registration number already exists.', 'danger')
            return render_template('buses/form.html', form=form, title='Edit Bus')

        bus.registration_number = form.registration_number.data
        bus.capacity = form.capacity.data
        bus.model = form.model.data
        bus.status = form.status.data
        bus.purchase_date = form.purchase_date.data

        db.session.commit()
        flash(f'Bus {bus.registration_number} updated successfully!', 'success')
        return redirect(url_for('buses.list_buses'))

    return render_template('buses/form.html', form=form, title='Edit Bus')

@buses_bp.route('/delete/<int:id>', methods=['POST'])
def delete_bus(id):
    """Delete a bus"""
    bus = Bus.query.get_or_404(id)

    # Check if bus is assigned to any schedules
    schedule_count = Schedule.query.filter_by(bus_id=id).count()
    if schedule_count > 0:
        flash(f'Cannot delete bus {bus.registration_number}. It is assigned to {schedule_count} schedule(s).', 'danger')
        return redirect(url_for('buses.list_buses'))

    db.session.delete(bus)
    db.session.commit()
    flash(f'Bus {bus.registration_number} deleted successfully!', 'success')
    return redirect(url_for('buses.list_buses'))
