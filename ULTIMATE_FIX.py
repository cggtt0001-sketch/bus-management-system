#!/usr/bin/env python3
"""
ULTIMATE FIX for the database issue
"""

import os
import sys
import sqlite3
import shutil
import subprocess
from datetime import datetime

def backup_database():
    """Backup current database"""
    db_files = ['bus_depot.db', 'bus_management.db']
    for db_file in db_files:
        if os.path.exists(db_file):
            backup_path = f"{db_file}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            shutil.copy(db_file, backup_path)
            print(f"✅ Backed up {db_file} to {backup_path}")

def clear_cache():
    """Clear Flask/SQLAlchemy cache"""
    print("🔧 Clearing Python cache...")

    cache_dirs = [
        '__pycache__',
        '__pycache__/**/*',
        'instance/__pycache__',
        'app/__pycache__'
    ]

    cache_cleared = False
    for cache_dir in cache_dirs:
        for root, dirs, files in os.walk(cache_dir):
            for file in files:
                if file.endswith(('.pyc'):
                    try:
                        os.remove(os.path.join(root, file))
                        cache_cleared = True
                    except:
                        pass

    if cache_cleared:
        print("✅ Cleared Python cache directories")

def delete_old_databases():
    """Remove problematic database files"""
    db_files = ['bus_depot.db', 'bus_management.db']
    for db_file in db_files:
        if os.path.exists(db_file):
            try:
                os.remove(db_file)
                print(f"🗑️ Deleted old database: {db_file}")
            except:
                pass

def create_fresh_database():
    """Create a completely fresh database with all required tables and GPS columns"""
    print("🔧 Creating fresh database with all tables...")

    conn = sqlite3.connect('bus_management.db')
    cursor = conn.cursor()

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

    # Create other required tables
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

    print("   ✅ Created all required tables")

    # Add sample data
    print("📊 Adding sample data...")

    # Routes
    cursor.executemany("""
        INSERT INTO routes (route_name, start_point, end_point, distance, stops)
        VALUES (?, ?, ?, ?, ?, ?)
    """, [
        ('Downtown Express', 'Central Station', 'Airport', 25.5, 'Main St, 5th Ave, Airport Rd'),
        ('City Circular', 'Bus Terminal', 'Bus Terminal', 15.0, 'All major city stops'),
        ('University Route', 'Campus North', 'Downtown', 8.2, 'Campus areas, shopping district'),
        ('Suburban Connector', 'Suburb Mall', 'City Center', 12.8, 'Residential areas, office park')
    ])

    # Crew
    cursor.executemany("""
        INSERT INTO crew (crew_id, name, role, contact_info, hire_date)
        VALUES (?, ?, ?, ?, ?, ?)
    """, [
        ('DRV001', 'John Smith', 'Driver', '555-0101', '2023-01-15'),
        ('DRV002', 'Sarah Johnson', 'Driver', '555-0102', '2023-02-20'),
        ('COND001', 'Mike Wilson', 'Commutator', '555-0103', '2023-03-10'),
        ('COND001', 'Emily Davis', 'Conductor', '555-0104', '2023-04-05')
    ])

    # Buses with GPS coordinates
    cursor.executemany("""
        INSERT INTO buses (registration_number, capacity, model, status, purchase_date, location_lat, location_lng, last_location_update)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, [
        ('BUS001', 45, 'Mercedes Citaro', 'active', '2023-01-01', 40.7128, -74.0060, datetime.now()),
        ('BUS002', 50, 'Volvo 7900', 'active', '2023-02-15', 40.7589, -73.9851, datetime.now()),
        ('BUS003', 40, 'MAN Lion\'s City', 'active', '2023-03-20', 40.7282, -73.9942, datetime.now()),
        ('BUS004', 55, 'Alexander Dennis', 'maintenance', '2022-12-01', None, None, None),
        ('BUS005', 35, 'Irisbus Crossway', 'inactive', '2022-10-15', None, None, None)
    ])

    # Schedules
    cursor.executemany("""
        INSERT INTO schedules (route_id, bus_id, departure_time, arrival_time, frequency, active)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, [
        (1, 1, '08:00:00', '17:00:00', 'daily', 1),
        (2, 2, '09:00:00', '18:00:00', 'daily', 1),
        (3, 3, '07:30:00', '16:30:00', 'daily', 1),
        (4, 1, '18:30:00', '23:00:00', 'daily', 1)
    ])

    # Crew assignments
    cursor.executemany("""
        INSERT INTO crew_assignments (schedule_id, crew_id, assignment_date, notes)
        VALUES (?, ?, ?, ?, ?)
    """, [
        (1, 1, '2025-01-01', 'Morning shift'),
        (1, 3, '2025-01-01', 'Morning shift'),
        (2, 2, '2025-01-01', 'Morning shift'),
        (2, 4, '2025-01-01', 'Morning shift'),
        (3, 1, '2025-01-01', 'Afternoon shift'),
        (3, 3, '2025-01-01', 'Afternoon shift'),
        (4, 2, '2025-01-01', 'Evening shift'),
        (4, 4, '2025-01-01', 'Evening shift')
    ])

    conn.commit()
    conn.close()

    print("✅ Fresh database created with all tables and GPS data")

def test_database():
    """Test the new database"""
    try:
        conn = sqlite3.connect('bus_management.db')
        cursor = conn.cursor()

        # Test basic query
        cursor.execute("SELECT COUNT(*) FROM buses")
        bus_count = cursor.fetchone()[0]
        print(f"   ✅ Database test: Found {bus_count} buses")

        # Test GPS columns
        cursor.execute("PRAGMA table_info(buses)")
        columns = [row[1] for row in cursor.fetchall()]
        gps_columns = ['location_lat', 'location_lng', 'last_location_update']

        missing_columns = [col for col in gps_columns if col not in columns]
        if missing_columns:
            print(f"   ❌ Still missing GPS columns: {missing_columns}")
            return False

        # Test the exact query
        cursor.execute("""
            SELECT b.id, b.registration_number, b.location_lat, b.location_lng, b.status
            FROM buses b
            WHERE b.status = 'active'
        """)
        results = cursor.fetchall()

        print(f"   ✅ Query test: Found {len(results)} active buses")

        if results:
            for i, (bus_id, reg_num, lat, lng, status) in enumerate(results):
                print(f"   🚌 {reg_num}: GPS({lat}, {lng}) - {status}")

        conn.close()
        return True

    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_flask_app():
    """Test the Flask app with the new database"""
    print("🧪 Testing Flask app...")

    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

        # Clear Python cache first
        clear_cache()

        # Try importing and creating Flask app
        from app import create_app

        app = create_app()

        print("   ✅ Flask app created successfully")

        with app.app_context():
            from app.models import db, Bus

            # Test basic query
            bus_count = Bus.query.count()
            print(f"   ✅ SQLAlchemy test: Found {bus_count} buses")

            # Test GPS query
            active_buses = Bus.query.filter_by(status='active').all()
            print(f"   ✅ GPS query test: Found {len(active_buses)} active buses")

            if active_buses:
                bus = active_buses[0]
                print(f"   ✅ Sample bus: {bus.registration_number} with GPS: ({bus.location_lat}, {bus.location_lng})")

            # Test the exact query from dashboard
            try:
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

                print(f"   ✅ Complex query test: Found {len(results)} results")

                if results:
                    bus, schedule, route, crew = results[0]
                    print(f"   ✅ Complex query sample: {bus.registration_number} on {route.route_name}")

                    # Test GPS coordinates
                    if hasattr(bus, 'location_lat') and bus.location_lat:
                        print(f"   🗺️  GPS: ({bus.location_lat}, {bus.location_lng})")

            except Exception as query_error:
                print(f"   ❌ Complex query failed: {query_error}")
                return False

        return True

    except Exception as flask_error:
        print(f"❌ Flask app error: {flask_error}")
        return False

def main():
    print("=" * 70)
    print("🔧 ULTIMATE FIX - Database Issue")
    print("=" * 70)

    # Step 1: Backup
    backup_database()

    # Step 2: Clear cache
    clear_cache()

    # Step 3: Delete old databases
    delete_old_databases()

    # Step 4: Create fresh database
    if create_fresh_database():

        # Step 5: Test database
        if test_database():
            print("\n✅ Database test passed!")

            # Step 6: Test Flask app
            if test_flask_app():
                print("\n✅ Flask app test passed!")
                print("\n🎉 COMPLETE SUCCESS!")
                print("\n🚀 Your Flask app should now work perfectly!")
                print("\n🗺️  Visit the map dashboard:")
                print("   http://localhost:5000/dashboard/map")

                print("\n📋 Next steps:")
                print("   1. Keep the app running (press Ctrl+C only when done)")
                print("   2. Test the map dashboard in your browser")
                print("   3. Report back here if there are still issues")

            else:
                print("\n❌ Flask app still has issues. This is unusual.")
                print("   The database is completely fixed, so there might be:")
                print("   - Import issues in the Flask app")
                print("   - Python path problems")
                print("   - Virtual environment issues")

        else:
            print("\n❌ Database creation failed!")

    print("\n" + "=" * 70)

if __name__name__ == "__main__":
    main()