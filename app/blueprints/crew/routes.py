from flask import render_template, redirect, url_for, flash, request
from app.blueprints.crew import crew_bp
from app.blueprints.crew.forms import CrewForm, CrewAssignmentForm
from app.models import Crew, CrewAssignment, Schedule, db
from sqlalchemy.exc import IntegrityError
from datetime import date

@crew_bp.route('/')
def list_crew():
    """List all crew members"""
    crew_members = Crew.query.all()
    return render_template('crew/list.html', crew_members=crew_members)

@crew_bp.route('/add', methods=['GET', 'POST'])
def add_crew():
    """Add a new crew member"""
    form = CrewForm()
    if form.validate_on_submit():
        try:
            crew = Crew(
                crew_id=form.crew_id.data,
                name=form.name.data,
                role=form.role.data,
                contact_info=form.contact_info.data,
                hire_date=form.hire_date.data
            )
            db.session.add(crew)
            db.session.commit()
            flash(f'Crew member {crew.name} added successfully!', 'success')
            return redirect(url_for('crew.list_crew'))
        except IntegrityError:
            db.session.rollback()
            flash('Crew ID already exists.', 'danger')
    return render_template('crew/form.html', form=form, title='Add New Crew Member')

@crew_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_crew(id):
    """Edit an existing crew member"""
    crew = Crew.query.get_or_404(id)
    form = CrewForm(obj=crew)
    form.crew_db_id = id

    if form.validate_on_submit():
        # Check crew_id uniqueness (excluding current crew)
        existing = Crew.query.filter_by(crew_id=form.crew_id.data).first()
        if existing and existing.id != id:
            flash('Crew ID already exists.', 'danger')
            return render_template('crew/form.html', form=form, title='Edit Crew Member')

        crew.crew_id = form.crew_id.data
        crew.name = form.name.data
        crew.role = form.role.data
        crew.contact_info = form.contact_info.data
        crew.hire_date = form.hire_date.data

        db.session.commit()
        flash(f'Crew member {crew.name} updated successfully!', 'success')
        return redirect(url_for('crew.list_crew'))

    return render_template('crew/form.html', form=form, title='Edit Crew Member')

@crew_bp.route('/delete/<int:id>', methods=['POST'])
def delete_crew(id):
    """Delete a crew member"""
    crew = Crew.query.get_or_404(id)

    # Check if crew has active assignments
    assignment_count = CrewAssignment.query.filter_by(crew_id=id).count()
    if assignment_count > 0:
        flash(f'Cannot delete crew member {crew.name}. They have {assignment_count} active assignment(s).', 'danger')
        return redirect(url_for('crew.list_crew'))

    db.session.delete(crew)
    db.session.commit()
    flash(f'Crew member {crew.name} deleted successfully!', 'success')
    return redirect(url_for('crew.list_crew'))

@crew_bp.route('/assignments')
def list_assignments():
    """View all crew assignments"""
    assignments = CrewAssignment.query.all()
    return render_template('crew/assignments.html', assignments=assignments)

@crew_bp.route('/assign', methods=['GET', 'POST'])
def assign_crew():
    """Assign crew to a schedule"""
    form = CrewAssignmentForm()

    # Get schedule_id from query parameter if provided
    schedule_id = request.args.get('schedule_id', type=int)

    # Populate schedule choices
    schedules = Schedule.query.filter_by(active=True).all()
    form.schedule_id.choices = [
        (s.id, f"{s.route.route_name} - {s.departure_time.strftime('%H:%M')} ({s.bus.registration_number})")
        for s in schedules
    ]

    # Populate crew choices
    crew_members = Crew.query.all()
    form.crew_id.choices = [
        (c.id, f"{c.name} ({c.role})")
        for c in crew_members
    ]

    # Pre-select schedule if provided
    if schedule_id and request.method == 'GET':
        form.schedule_id.data = schedule_id

    # Set default assignment date to today
    if not form.assignment_date.data:
        form.assignment_date.data = date.today()

    if form.validate_on_submit():
        # Check if crew already assigned to this schedule on this date
        existing = CrewAssignment.query.filter_by(
            schedule_id=form.schedule_id.data,
            crew_id=form.crew_id.data,
            assignment_date=form.assignment_date.data
        ).first()

        if existing:
            flash('Crew member is already assigned to this schedule on this date.', 'danger')
            return render_template('crew/assign_form.html', form=form, title='Assign Crew to Schedule')

        assignment = CrewAssignment(
            schedule_id=form.schedule_id.data,
            crew_id=form.crew_id.data,
            assignment_date=form.assignment_date.data,
            notes=form.notes.data
        )
        db.session.add(assignment)
        db.session.commit()
        flash('Crew assigned successfully!', 'success')
        return redirect(url_for('crew.list_assignments'))

    return render_template('crew/assign_form.html', form=form, title='Assign Crew to Schedule')

@crew_bp.route('/assignments/delete/<int:id>', methods=['POST'])
def delete_assignment(id):
    """Delete a crew assignment"""
    assignment = CrewAssignment.query.get_or_404(id)
    db.session.delete(assignment)
    db.session.commit()
    flash('Assignment removed successfully!', 'success')
    return redirect(url_for('crew.list_assignments'))
