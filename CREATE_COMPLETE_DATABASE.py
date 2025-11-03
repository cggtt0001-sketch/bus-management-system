#!/usr/bin/env python3
"""
Create a complete database for SQLAlchemy to use
"""

import sqlite3
import os
import shutil
from datetime import datetime
import random

def create_complete_database(db_path):
    """Create a complete database with all tables and data"""

    print(f"🔧 Creating complete database: {db_path}")
    print("=" * 50)

    # Backup existing database if it exists
    if os.path.exists(db_path):
        backup_path = db_path + f'.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
        shutil.copy(db_path, backup_path)
        print(f"✅ Backed up existing database to: {backup_path}")

    # Create new database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("📋 Creating tables...")

    # Create buses table WITH GPS columns
    cursor.execute("""
        CREATE TABLE buses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            registration_number VARCHAR(50) UNIQUE NOT NULL,
            capacity INTEGER NOT NULL,
            model VARCHAR(100),
            status VARCHAR(20) DEFAULT 'active',
            purchase_date DATE,
            location_lat REAL,
            location_lng REAL,
            last_location_update DATETIME
        )
    """)
    print("   ✅ Created buses table with GPS columns")

    # Create routes table
    cursor.execute("""
        CREATE TABLE routes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            route_name VARCHAR(100) UNIQUE NOT NULL,
            start_point VARCHAR(100) NOT NULL,
            end_point VARCHAR(100) NOT NULL,
            distance REAL NOT NULL,
            stops TEXT
        )
    """)
    print("   ✅ Created routes table")

    # Create crew table
    cursor.execute("""
        CREATE TABLE crew (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            crew_id VARCHAR(20) UNIQUE NOT NULL,
            name VARCHAR(100) NOT NULL,
            role VARCHAR(30) NOT NULL,
            contact_info VARCHAR(100) NOT NULL,
            hire_date DATE
        )
    """)
    print("   ✅ Created crew table")

    # Create schedules table
    cursor.execute("""
        CREATE TABLE schedules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            route_id INTEGER NOT NULL,
            bus_id INTEGER NOT NULL,
            departure_time TIME NOT NULL,
            arrival_time TIME NOT NULL,
            frequency VARCHAR(20) NOT NULL,
            active BOOLEAN DEFAULT 1,
            FOREIGN KEY (route_id) REFERENCES routes (id),
            FOREIGN KEY (bus_id) REFERENCES buses (id)
        )
    """)
    print("   ✅ Created schedules table")

    # Create crew_assignments table
    cursor.execute("""
        CREATE TABLE crew_assignments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            schedule_id INTEGER NOT NULL,
            crew_id INTEGER NOT NULL,
            assignment_date DATE NOT NULL,
            notes TEXT,
            FOREIGN KEY (schedule_id) REFERENCES schedules (id),
            FOREIGN KEY (crew_id) REFERENCES crew (id)
        )
    """)
    print("   ✅ Created crew_assignments table")

    # Create working_hours table
    cursor.execute("""
        CREATE TABLE working_hours (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            crew_id INTEGER NOT NULL,
            date DATE NOT NULL,
            hours_worked REAL NOT NULL,
            schedule_id INTEGER,
            FOREIGN KEY (crew_id) REFERENCES crew (id),
            FOREIGN KEY (schedule_id) REFERENCES schedules (id)
        )
    """)
    print("   ✅ Created working_hours table")

    print("\n📊 Adding sample data...")

    # Sample routes
    routes_data = [
        ('Downtown Express', 'Central Station', 'Airport', 25.5, 'Main St, 5th Ave, Airport Rd'),
        ('City Circular', 'Bus Terminal', 'Bus Terminal', 15.0, 'All major city stops'),
        ('University Route', 'Campus North', 'Downtown', 8.2, 'Campus areas, shopping district'),
        ('Suburban Connector', 'Suburb Mall', 'City Center', 12.8, 'Residential areas, office park')
    ]
    cursor.executemany("INSERT INTO routes (route_name, start_point, end_point, distance, stops) VALUES (?, ?, ?, ?, ?)", routes_data)
    print(f"   ✅ Added {len(routes_data)} routes")

    # Sample crew
    crew_data = [
        ('DRV001', 'John Smith', 'Driver', '555-0101', '2023-01-15'),
        ('DRV002', 'Sarah Johnson', 'Driver', '555-0102', '2023-02-20'),
        ('DRV003', 'Mike Wilson', 'Driver', '555-0103', '2023-03-10'),
        ('COND001', 'Emily Davis', 'Conductor', '555-0104', '2023-04-05'),
        ('COND002', 'Robert Brown', 'Conductor', '555-0105', '2023-05-15')
    ]
    cursor.executemany("INSERT INTO crew (crew_id, name, role, contact_info, hire_date) VALUES (?, ?, ?, ?, ?)", crew_data)
    print(f"   ✅ Added {len(crew_data)} crew members")

    # Sample buses with GPS coordinates
    buses_data = [
        ('BUS001', 45, 'Mercedes Citaro', 'active', '2023-01-01', 40.7128, -74.0060, datetime.now()),
        ('BUS002', 50, 'Volvo 7900', 'active', '2023-02-15', 40.7589, -73.9851, datetime.now()),
        ('BUS003', 40, 'MAN Lion\'s City', 'active', '2023-03-20', 40.7282, -73.9942, datetime.now()),
        ('BUS004', 55, 'Alexander Dennis', 'maintenance', '2022-12-01', None, None, None),
        ('BUS005', 35, 'Irisbus Crossway', 'inactive', '2022-10-15', None, None, None)
    ]
    cursor.executemany("INSERT INTO buses (registration_number, capacity, model, status, purchase_date, location_lat, location_lng, last_location_update) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", buses_data)
    print(f"   ✅ Added {len(buses_data)} buses with GPS coordinates")

    # Sample schedules
    schedules_data = [
        (1, 1, '08:00:00', '17:00:00', 'daily', 1),
        (2, 2, '09:00:00', '18:00:00', 'daily', 1),
        (3, 3, '07:30:00', '16:30:00', 'daily', 1),
        (4, 1, '18:30:00', '23:00:00', 'daily', 1)
    ]
    cursor.executemany("INSERT INTO schedules (route_id, bus_id, departure_time, arrival_time, frequency, active) VALUES (?, ?, ?, ?, ?, ?)", schedules_data)
    print(f"   ✅ Added {len(schedules_data)} schedules")

    # Sample crew assignments
    assignments_data = [
        (1, 1, '2025-01-01', 'Morning shift'),
        (1, 3, '2025-01-01', 'Morning shift'),
        (2, 2, '2025-01-01', 'Morning shift'),
        (2, 4, '2025-01-01', 'Morning shift'),
        (3, 1, '2025-01-01', 'Afternoon shift'),
        (3, 3, '2025-01-01', 'Afternoon shift'),
        (4, 2, '2025-01-01', 'Evening shift'),
        (4, 4, '2025-01-01', 'Evening shift')
    ]
    cursor.executemany("INSERT INTO crew_assignments (schedule_id, crew_id, assignment_date, notes) VALUES (?, ?, ?, ?)", assignments_data)
    print(f"   ✅ Added {len(assignments_data)} crew assignments")

    # Sample working hours
    working_hours_data = []
    for crew_id in range(1, 6):  # 5 crew members
        for day in range(1, 31):  # 30 days of sample data
            hours = round(random.uniform(6, 10), 1)
            working_hours_data.append((crew_id, f'2025-01-{day:02d}', hours, None))

    cursor.executemany("INSERT INTO working_hours (crew_id, date, hours_worked, schedule_id) VALUES (?, ?, ?, ?)", working_hours_data)
    print(f"   ✅ Added {len(working_hours_data)} working hours records")

    conn.commit()
    conn.close()

    print(f"\n🎉 Complete database created: {db_path}")
    return True

def test_database(db_path):
    """Test the database"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Test table existence
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        required_tables = ['buses', 'routes', 'crew', 'schedules', 'crew_assignments', 'working_hours']

        missing_tables = [table for table in required_tables if table not in tables]
        if missing_tables:
            print(f"❌ Missing tables: {missing_tables}")
            return False

        print(f"✅ All required tables exist: {required_tables}")

        # Test GPS columns
        cursor.execute("PRAGMA table_info(buses)")
        columns = [row[1] for row in cursor.fetchall()]
        gps_columns = ['location_lat', 'location_lng', 'last_location_update']

        missing_columns = [col for col in gps_columns if col not in columns]
        if missing_columns:
            print(f"❌ Missing GPS columns: {missing_columns}")
            return False

        print(f"✅ All GPS columns exist: {gps_columns}")

        # Test data
        cursor.execute("SELECT COUNT(*) FROM buses WHERE status='active' AND location_lat IS NOT NULL")
        gps_buses = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM buses")
        total_buses = cursor.fetchone()[0]

        print(f"✅ Database contains {total_buses} buses, {gps_buses} with GPS coordinates")

        conn.close()
        return True

    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_flask_app():
    """Test Flask app with the new database"""
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from app import create_app

        app = create_app()
        with app.app_context():
            from app.models import db, Bus

            # Test basic query
            bus_count = Bus.query.count()
            print(f"✅ Flask app test: Found {bus_count} buses")

            # Test active buses query
            active_buses = Bus.query.filter_by(status='active').all()
            print(f"✅ Active buses query: Found {len(active_buses)} active buses")

            # Test GPS data
            if active_buses:
                bus = active_buses[0]
                print(f"✅ GPS data test: {bus.registration_number} at ({bus.location_lat}, {bus.location_lng})")

            # Test the complex query from dashboard
            results = db.session.query(Bus, Schedule, Route, Crew).join(
                Schedule, Bus.id == Schedule.bus_id
            ).join(
                Route, Schedule.route_id == Route.id
            ).join(
                CrewAssignment, Schedule.id == CrewAssignment.schedule_id
            ).join(
                Crew, CrewAssignment.crew_id == Crew.id
            ).filter(
                Bus.status == 'active',
                Schedule.active == True
            ).all()

            print(f"✅ Complex query test: Found {len(results)} results")

        return True

    except Exception as e:
        print(f"❌ Flask app test failed: {e}")
        return False

def main():
    print("=" * 70)
    print("🔧 CREATING COMPLETE DATABASE FOR SQLALCHEMY")
    print("=" * 70)

    db_path = 'bus_management.db'

    # Create complete database
    if create_complete_database(db_path):
        print("\n📋 Testing the created database...")
        if test_database(db_path):
            print("✅ Database test passed!")
        else:
            print("❌ Database test failed!")
            return

        print("\n📋 Testing Flask app...")
        if test_flask_app():
            print("✅ Flask app test passed!")
        else:
            print("❌ Flask app test failed!")
            return

        print("\n🎉 SUCCESS!")
        print("🚀 Your Flask app should now work perfectly!")
        print("\nTo start the application:")
        print("   python run.py")
        print("\nThen visit the map dashboard:")
        print("   http://localhost:5000/dashboard/map")

    else:
        print("❌ Failed to create database")

    print("\n" + "=" * 70)

if __name__ == "__main__":
    main()