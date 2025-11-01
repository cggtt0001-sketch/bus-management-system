from flask import render_template, redirect, url_for, flash, request
from app.blueprints.buses import buses_bp
from app.blueprints.buses.forms import BusForm
from app.models import Bus, Schedule, db
from sqlalchemy.exc import IntegrityError

@buses_bp.route('/')
def list_buses():
    """List all buses"""
    buses = Bus.query.all()
    return render_template('buses/list.html', buses=buses)

@buses_bp.route('/add', methods=['GET', 'POST'])
def add_bus():
    """Add a new bus"""
    form = BusForm()
    if form.validate_on_submit():
        try:
            bus = Bus(
                registration_number=form.registration_number.data,
                capacity=form.capacity.data,
                model=form.model.data,
                status=form.status.data,
                purchase_date=form.purchase_date.data
            )
            db.session.add(bus)
            db.session.commit()
            flash(f'Bus {bus.registration_number} added successfully!', 'success')
            return redirect(url_for('buses.list_buses'))
        except IntegrityError:
            db.session.rollback()
            flash('Registration number already exists.', 'danger')
    return render_template('buses/form.html', form=form, title='Add New Bus')

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
