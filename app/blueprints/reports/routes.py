from flask import render_template
from app.blueprints.reports import reports_bp
from app.blueprints.reports.utils import generate_csv, generate_pdf
from app.models import Schedule, Route, Bus, Crew, CrewAssignment, db
from datetime import date
from sqlalchemy import func

@reports_bp.route('/')
def index():
    """Reports homepage with links to different reports"""
    return render_template('reports/index.html')

# ==================== Daily Schedules Report ====================

@reports_bp.route('/daily-schedules')
def daily_schedules():
    """View daily schedules report"""
    schedules = Schedule.query.filter_by(active=True).all()
    return render_template('reports/daily_schedules.html', schedules=schedules, report_date=date.today())

@reports_bp.route('/daily-schedules/export/csv')
def daily_schedules_csv():
    """Export daily schedules to CSV"""
    schedules = Schedule.query.filter_by(active=True).all()

    headers = ['Route', 'Bus', 'Departure', 'Arrival', 'Frequency', 'Assigned Crew']
    data = []

    for schedule in schedules:
        # Get assigned crew for this schedule
        crew_list = CrewAssignment.query.filter_by(schedule_id=schedule.id).all()
        crew_names = ', '.join([ca.crew_member.name for ca in crew_list]) if crew_list else 'None'

        data.append({
            'Route': schedule.route.route_name,
            'Bus': schedule.bus.registration_number,
            'Departure': schedule.departure_time.strftime('%H:%M'),
            'Arrival': schedule.arrival_time.strftime('%H:%M'),
            'Frequency': schedule.frequency.capitalize(),
            'Assigned Crew': crew_names
        })

    filename = f"daily_schedules_{date.today().strftime('%Y%m%d')}.csv"
    return generate_csv(data, headers, filename)

@reports_bp.route('/daily-schedules/export/pdf')
def daily_schedules_pdf():
    """Export daily schedules to PDF"""
    schedules = Schedule.query.filter_by(active=True).all()

    headers = ['Route', 'Bus', 'Departure', 'Arrival', 'Frequency', 'Crew']
    data = []

    for schedule in schedules:
        # Get assigned crew for this schedule
        crew_list = CrewAssignment.query.filter_by(schedule_id=schedule.id).all()
        crew_names = ', '.join([ca.crew_member.name for ca in crew_list]) if crew_list else 'None'

        data.append([
            schedule.route.route_name,
            schedule.bus.registration_number,
            schedule.departure_time.strftime('%H:%M'),
            schedule.arrival_time.strftime('%H:%M'),
            schedule.frequency.capitalize(),
            crew_names
        ])

    title = "Daily Schedules Report"
    date_str = date.today().strftime('%Y-%m-%d')
    filename = f"daily_schedules_{date.today().strftime('%Y%m%d')}.pdf"

    return generate_pdf(title, date_str, data, headers, filename)

# ==================== Crew Assignments Report ====================

@reports_bp.route('/crew-assignments')
def crew_assignments():
    """View crew assignments report"""
    assignments = CrewAssignment.query.all()
    return render_template('reports/crew_assignments.html', assignments=assignments, report_date=date.today())

@reports_bp.route('/crew-assignments/export/csv')
def crew_assignments_csv():
    """Export crew assignments to CSV"""
    assignments = CrewAssignment.query.all()

    headers = ['Crew ID', 'Crew Name', 'Role', 'Schedule', 'Assignment Date']
    data = []

    for assignment in assignments:
        schedule_info = f"{assignment.schedule.route.route_name} - {assignment.schedule.departure_time.strftime('%H:%M')}"

        data.append({
            'Crew ID': assignment.crew_member.crew_id,
            'Crew Name': assignment.crew_member.name,
            'Role': assignment.crew_member.role,
            'Schedule': schedule_info,
            'Assignment Date': assignment.assignment_date.strftime('%Y-%m-%d')
        })

    filename = f"crew_assignments_{date.today().strftime('%Y%m%d')}.csv"
    return generate_csv(data, headers, filename)

@reports_bp.route('/crew-assignments/export/pdf')
def crew_assignments_pdf():
    """Export crew assignments to PDF"""
    assignments = CrewAssignment.query.all()

    headers = ['Crew ID', 'Name', 'Role', 'Schedule', 'Date']
    data = []

    for assignment in assignments:
        schedule_info = f"{assignment.schedule.route.route_name} - {assignment.schedule.departure_time.strftime('%H:%M')}"

        data.append([
            assignment.crew_member.crew_id,
            assignment.crew_member.name,
            assignment.crew_member.role,
            schedule_info,
            assignment.assignment_date.strftime('%Y-%m-%d')
        ])

    title = "Crew Assignments Report"
    date_str = date.today().strftime('%Y-%m-%d')
    filename = f"crew_assignments_{date.today().strftime('%Y%m%d')}.pdf"

    return generate_pdf(title, date_str, data, headers, filename)

# ==================== Route Performance Report ====================

@reports_bp.route('/route-performance')
def route_performance():
    """View route performance summary"""
    # Query routes with schedule counts
    route_data = db.session.query(
        Route,
        func.count(Schedule.id).label('schedule_count')
    ).outerjoin(Schedule).group_by(Route.id).all()

    return render_template('reports/route_performance.html', route_data=route_data, report_date=date.today())

@reports_bp.route('/route-performance/export/csv')
def route_performance_csv():
    """Export route performance to CSV"""
    route_data = db.session.query(
        Route,
        func.count(Schedule.id).label('schedule_count')
    ).outerjoin(Schedule).group_by(Route.id).all()

    headers = ['Route Name', 'Start Point', 'End Point', 'Distance (km)', 'Total Schedules', 'Utilization']
    data = []

    for route, schedule_count in route_data:
        # Simple utilization metric (schedules per route)
        utilization = f"{schedule_count} schedule(s)"

        data.append({
            'Route Name': route.route_name,
            'Start Point': route.start_point,
            'End Point': route.end_point,
            'Distance (km)': f"{route.distance:.1f}",
            'Total Schedules': schedule_count,
            'Utilization': utilization
        })

    filename = f"route_performance_{date.today().strftime('%Y%m%d')}.csv"
    return generate_csv(data, headers, filename)

@reports_bp.route('/route-performance/export/pdf')
def route_performance_pdf():
    """Export route performance to PDF"""
    route_data = db.session.query(
        Route,
        func.count(Schedule.id).label('schedule_count')
    ).outerjoin(Schedule).group_by(Route.id).all()

    headers = ['Route', 'Start', 'End', 'Distance', 'Schedules']
    data = []

    for route, schedule_count in route_data:
        data.append([
            route.route_name,
            route.start_point,
            route.end_point,
            f"{route.distance:.1f} km",
            str(schedule_count)
        ])

    title = "Route Performance Summary"
    date_str = date.today().strftime('%Y-%m-%d')
    filename = f"route_performance_{date.today().strftime('%Y%m%d')}.pdf"

    return generate_pdf(title, date_str, data, headers, filename)
