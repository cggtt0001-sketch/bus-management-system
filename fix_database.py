"""
Fix database issues for users encountering location field errors
This script will:
1. Find the correct database file
2. Add missing location columns if needed
3. Add sample data if the database is empty
4. Ensure all tables have the correct structure
"""

import sqlite3
import os
from datetime import datetime
import random

def find_database():
    """Find the database file in common locations"""
    possible_paths = [
        'bus_depot.db',
        'instance/bus_depot.db',
        'app.db',
        'database.db',
        '../bus_depot.db',
        '../instance/bus_depot.db'
    ]

    for path in possible_paths:
        if os.path.exists(path):
            print(f"Found database at: {path}")
            return path

    print("No existing database found. Will create a new one.")
    return None

def create_complete_database(db_path):
    """Create a complete database with all required tables and sample data"""

    print(f"Creating complete database at: {db_path}")

    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Drop existing tables if they exist (clean start)
        cursor.execute("DROP TABLE IF EXISTS working_hours")
        cursor.execute("DROP TABLE IF EXISTS crew_assignments")
        cursor.execute("DROP TABLE IF EXISTS schedules")
        cursor.execute("DROP TABLE IF EXISTS crew")
        cursor.execute("DROP TABLE IF EXISTS routes")
        cursor.execute("DROP TABLE IF EXISTS buses")

        # Create buses table with all required fields
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

        # Insert sample routes
        routes_data = [
            ('Downtown Express', 'Central Station', 'Airport', 25.5, 'Main St, 5th Ave, Airport Rd'),
            ('City Circular', 'Bus Terminal', 'Bus Terminal', 15.0, 'All major city stops'),
            ('University Route', 'Campus North', 'Downtown', 8.2, 'Campus areas, shopping district'),
            ('Suburban Connector', 'Suburb Mall', 'City Center', 12.8, 'Residential areas, office park')
        ]
        cursor.executemany("INSERT INTO routes (route_name, start_point, end_point, distance, stops) VALUES (?, ?, ?, ?, ?)", routes_data)

        # Insert sample crew
        crew_data = [
            ('DRV001', 'John Smith', 'Driver', '555-0101', '2023-01-15'),
            ('DRV002', 'Sarah Johnson', 'Driver', '555-0102', '2023-02-20'),
            ('COND001', 'Mike Wilson', 'Conductor', '555-0103', '2023-03-10'),
            ('COND002', 'Emily Davis', 'Conductor', '555-0104', '2023-04-05'),
            ('MAINT001', 'Robert Brown', 'Maintenance Staff', '555-0105', '2023-01-20')
        ]
        cursor.executemany("INSERT INTO crew (crew_id, name, role, contact_info, hire_date) VALUES (?, ?, ?, ?, ?)", crew_data)

        # Insert sample buses with GPS coordinates
        buses_data = [
            ('BUS001', 45, 'Mercedes Citaro', 'active', '2023-01-01', 40.7128, -74.0060, datetime.now()),
            ('BUS002', 50, 'Volvo 7900', 'active', '2023-02-15', 40.7589, -73.9851, datetime.now()),
            ('BUS003', 40, 'MAN Lion\'s City', 'active', '2023-03-20', 40.7282, -73.9942, datetime.now()),
            ('BUS004', 55, 'Alexander Dennis', 'maintenance', '2022-12-01', None, None, None),
            ('BUS005', 35, 'Irisbus Crossway', 'inactive', '2022-10-15', None, None, None)
        ]
        cursor.executemany("INSERT INTO buses (registration_number, capacity, model, status, purchase_date, location_lat, location_lng, last_location_update) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", buses_data)

        # Insert sample schedules
        schedules_data = [
            (1, 1, '08:00:00', '17:00:00', 'daily', 1),
            (2, 2, '09:00:00', '18:00:00', 'daily', 1),
            (3, 3, '07:30:00', '16:30:00', 'daily', 1),
            (1, 1, '18:30:00', '23:00:00', 'daily', 1)
        ]
        cursor.executemany("INSERT INTO schedules (route_id, bus_id, departure_time, arrival_time, frequency, active) VALUES (?, ?, ?, ?, ?, ?)", schedules_data)

        # Insert sample crew assignments
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

        # Insert sample working hours
        working_hours_data = []
        for crew_id in range(1, 6):
            for day in range(1, 31):
                hours = round(random.uniform(6, 10), 1)
                working_hours_data.append((crew_id, f'2025-01-{day:02d}', hours, None))

        cursor.executemany("INSERT INTO working_hours (crew_id, date, hours_worked, schedule_id) VALUES (?, ?, ?, ?)", working_hours_data)

        conn.commit()
        conn.close()

        print("✅ Complete database created successfully!")
        return True

    except Exception as e:
        print(f"❌ Error creating database: {e}")
        if conn:
            conn.close()
        return False

def fix_existing_database(db_path):
    """Fix an existing database by adding missing columns"""

    print(f"Fixing existing database: {db_path}")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Check buses table structure
        cursor.execute("PRAGMA table_info(buses)")
        columns = [row[1] for row in cursor.fetchall()]

        # Add missing columns
        if 'location_lat' not in columns:
            cursor.execute("ALTER TABLE buses ADD COLUMN location_lat REAL")
            print("✅ Added location_lat column")

        if 'location_lng' not in columns:
            cursor.execute("ALTER TABLE buses ADD COLUMN location_lng REAL")
            print("✅ Added location_lng column")

        if 'last_location_update' not in columns:
            cursor.execute("ALTER TABLE buses ADD COLUMN last_location_update DATETIME")
            print("✅ Added last_location_update column")

        # Check if working_hours table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='working_hours'")
        if not cursor.fetchone():
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
            print("✅ Created working_hours table")

        # Update active buses with GPS coordinates
        cursor.execute("""
            UPDATE buses
            SET location_lat = 40.7128 + (RANDOM() % 1000 - 500) * 0.0001,
                location_lng = -74.0060 + (RANDOM() % 1000 - 500) * 0.0001,
                last_location_update = datetime('now')
            WHERE status = 'active' AND location_lat IS NULL
        """)
        updated = cursor.rowcount
        print(f"✅ Updated {updated} active buses with GPS coordinates")

        conn.commit()
        conn.close()

        print("✅ Database fixed successfully!")
        return True

    except Exception as e:
        print(f"❌ Error fixing database: {e}")
        if conn:
            conn.close()
        return False

def verify_database(db_path):
    """Verify that the database has all required structure"""

    if not os.path.exists(db_path):
        print(f"❌ Database file not found: {db_path}")
        return False

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Check tables exist
        required_tables = ['buses', 'routes', 'crew', 'schedules', 'crew_assignments', 'working_hours']

        for table in required_tables:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
            if not cursor.fetchone():
                print(f"❌ Missing table: {table}")
                conn.close()
                return False

        # Check buses table columns
        cursor.execute("PRAGMA table_info(buses)")
        columns = [row[1] for row in cursor.fetchall()]
        required_columns = ['registration_number', 'capacity', 'model', 'status', 'location_lat', 'location_lng', 'last_location_update']

        for col in required_columns:
            if col not in columns:
                print(f"❌ Missing column in buses table: {col}")
                conn.close()
                return False

        # Check for some data
        cursor.execute("SELECT COUNT(*) FROM buses")
        bus_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM buses WHERE status='active' AND location_lat IS NOT NULL")
        active_with_gps = cursor.fetchone()[0]

        print(f"✅ Database verification passed!")
        print(f"   🚌 Total buses: {bus_count}")
        print(f"   📍 Active buses with GPS: {active_with_gps}")

        conn.close()
        return True

    except Exception as e:
        print(f"❌ Database verification failed: {e}")
        if conn:
            conn.close()
        return False

if __name__ == "__main__":
    print("=" * 70)
    print("🚌 Bus Depot Management System - Database Fix Tool")
    print("=" * 70)

    # Find or create database
    db_path = find_database()

    if not db_path:
        # Create new database
        db_path = 'bus_depot.db'
        if create_complete_database(db_path):
            print("\n🎉 Database created and verified!")
        else:
            print("\n❌ Failed to create database!")
            exit(1)
    else:
        # Fix existing database
        if fix_existing_database(db_path):
            print("\n🎉 Database fixed!")
        else:
            print("\n❌ Failed to fix database!")
            exit(1)

    # Verify the database
    if verify_database(db_path):
        print("\n✅ All checks passed! The application should now work correctly.")
        print("\n🚀 Run the application with:")
        print("   python run.py")
        print("\n🗺️  Access the Live Map at:")
        print("   http://localhost:5000/dashboard/map")
        print("\n" + "=" * 70)
    else:
        print("\n❌ Database verification failed!")
        exit(1)