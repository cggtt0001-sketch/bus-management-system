from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import db, Bus, Schedule

bus_bp = Blueprint('bus', __name__, url_prefix='/bus')

@bus_bp.route('/list')
def list_buses():
    """Display all buses"""
    buses = Bus.query.all()
    return render_template('buses.html', buses=buses)

@bus_bp.route('/create', methods=['POST'])
def create_bus():
    """Create a new bus"""
    bus_number = request.form.get('bus_number', '').strip()

    # Validate bus_number
    if not bus_number:
        flash('Bus number is required', 'danger')
        return redirect(url_for('bus.list_buses'))

    if len(bus_number) > 50:
        flash('Bus number must be 50 characters or less', 'danger')
        return redirect(url_for('bus.list_buses'))

    # Check uniqueness
    existing_bus = Bus.query.filter_by(bus_number=bus_number).first()
    if existing_bus:
        flash('Bus number already exists', 'danger')
        return redirect(url_for('bus.list_buses'))

    # Create bus
    try:
        new_bus = Bus(bus_number=bus_number)
        db.session.add(new_bus)
        db.session.commit()
        flash('Bus created successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Database error occurred', 'danger')

    return redirect(url_for('bus.list_buses'))

@bus_bp.route('/update/<int:id>', methods=['POST'])
def update_bus(id):
    """Update an existing bus"""
    bus = Bus.query.get(id)
    if not bus:
        flash('Bus not found', 'danger')
        return redirect(url_for('bus.list_buses'))

    bus_number = request.form.get('bus_number', '').strip()

    # Validate bus_number
    if not bus_number:
        flash('Bus number is required', 'danger')
        return redirect(url_for('bus.list_buses'))

    if len(bus_number) > 50:
        flash('Bus number must be 50 characters or less', 'danger')
        return redirect(url_for('bus.list_buses'))

    # Check uniqueness (excluding current record)
    existing_bus = Bus.query.filter(Bus.bus_number == bus_number, Bus.id != id).first()
    if existing_bus:
        flash('Bus number already exists', 'danger')
        return redirect(url_for('bus.list_buses'))

    # Update bus
    try:
        bus.bus_number = bus_number
        db.session.commit()
        flash('Bus updated successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Database error occurred', 'danger')

    return redirect(url_for('bus.list_buses'))

@bus_bp.route('/delete/<int:id>', methods=['POST'])
def delete_bus(id):
    """Delete a bus with undo capability"""
    bus = Bus.query.get(id)
    if not bus:
        flash('Bus not found', 'danger')
        return redirect(url_for('bus.list_buses'))

    # Check if bus is used in any schedules
    existing_schedule = Schedule.query.filter_by(bus_id=id).first()
    if existing_schedule:
        flash('Cannot delete bus with existing schedules', 'danger')
        return redirect(url_for('bus.list_buses'))

    # Store bus data in session for undo
    session['last_deleted_bus'] = {
        'id': bus.id,
        'bus_number': bus.bus_number
    }

    try:
        db.session.delete(bus)
        db.session.commit()
        flash('Bus deleted successfully. <a href="/bus/undo" class="btn btn-sm btn-warning">Undo</a>', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Database error occurred', 'danger')

    return redirect(url_for('bus.list_buses'))

@bus_bp.route('/undo')
def undo_delete():
    """Restore last deleted bus"""
    if 'last_deleted_bus' not in session:
        flash('Nothing to undo', 'danger')
        return redirect(url_for('bus.list_buses'))

    deleted_data = session.pop('last_deleted_bus')

    try:
        # Re-insert with original ID
        new_bus = Bus(
            id=deleted_data['id'],
            bus_number=deleted_data['bus_number']
        )
        db.session.add(new_bus)
        db.session.commit()
        flash('Bus restored successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Database error occurred', 'danger')

    return redirect(url_for('bus.list_buses'))
