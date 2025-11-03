#!/usr/bin/env python3
"""
Fix SQLAlchemy database configuration issue
"""

import sqlite3
import os
import shutil
from datetime import datetime

def find_sqlalchemy_database():
    """Find which database SQLAlchemy is actually using"""

    print("🔍 Finding SQLAlchemy database configuration...")
    print("=" * 50)

    # Check config.py for database path
    config_paths = [
        'config.py',
        '../config.py',
        'app/config.py'
    ]

    db_path = None
    for config_path in config_paths:
        if os.path.exists(config_path):
            print(f"📁 Found config file: {config_path}")
            with open(config_path, 'r') as f:
                content = f.read()
                if 'SQLALCHEMY_DATABASE_URI' in content:
                    lines = content.split('\n')
                    for line in lines:
                        if 'SQLALCHEMY_DATABASE_URI' in line and 'sqlite' in line:
                            if 'sqlite:///' in line:
                                db_file = line.split('sqlite:///')[1].split("'")[0]
                                print(f"📍 SQLAlchemy database path: {db_file}")
                                db_path = db_file
                                break
                    break

    if db_path:
        return db_path
    else:
        return 'bus_depot.db'  # Default

def fix_sqlalchemy_database(sqlalchemy_db_path):
    """Fix the database that SQLAlchemy is actually using"""

    print(f"\n🔧 Fixing SQLAlchemy database: {sqlalchemy_db_path}")
    print("=" * 50)

    # Backup existing database if it exists
    if os.path.exists(sqlalchemy_db_path):
        backup_path = sqlalchemy_db_path + '.backup'
        shutil.copy(sqlalchemy_db_path, backup_path)
        print(f"✅ Backed up existing database to: {backup_path}")

    try:
        conn = sqlite3.connect(sqlalchemy_db_path)
        cursor = conn.cursor()

        # Check current schema
        cursor.execute("PRAGMA table_info(buses)")
        columns = [row[1] for row in cursor.fetchall()]

        # Check if GPS columns exist
        required_columns = ['location_lat', 'location_lng', 'last_location_update']
        missing_columns = [col for col in required_columns if col not in columns]

        if missing_columns:
            print(f"🔧 Adding missing columns: {missing_columns}")

            # Add missing columns
            for col in missing_columns:
                if col == 'location_lat':
                    cursor.execute("ALTER TABLE buses ADD COLUMN location_lat REAL")
                elif col == 'location_lng':
                    cursor.execute("ALTER TABLE buses ADD COLUMN location_lng REAL")
                elif col == 'last_location_update':
                    cursor.execute("ALTER TABLE buses ADD COLUMN last_location_update DATETIME")
                print(f"   ✅ Added {col}")

            print("✅ Missing columns added successfully")

        else:
            print("✅ All required columns already exist")

        # Create other necessary tables if they don't exist
        tables_to_create = [
            """
            CREATE TABLE IF NOT EXISTS routes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                route_name VARCHAR(100) UNIQUE NOT NULL,
                start_point VARCHAR(100) NOT NULL,
                end_point VARCHAR(100) NOT NULL,
                distance REAL NOT NULL,
                stops TEXT
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS crew (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                crew_id VARCHAR(20) UNIQUE NOT NULL,
                name VARCHAR(100) NOT NULL,
                role VARCHAR(30) NOT NULL,
                contact_info VARCHAR(100) NOT NULL,
                hire_date DATE
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS schedules (
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
            """,
            """
            CREATE TABLE IF NOT EXISTS crew_assignments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                schedule_id INTEGER NOT NULL,
                crew_id INTEGER NOT NULL,
                assignment_date DATE NOT NULL,
                notes TEXT,
                FOREIGN KEY (schedule_id) REFERENCES schedules (id),
                FOREIGN KEY (crew_id) REFERENCES crew (id)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS working_hours (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                crew_id INTEGER NOT NULL,
                date DATE NOT NULL,
                hours_worked REAL NOT NULL,
                schedule_id INTEGER,
                FOREIGN KEY (crew_id) REFERENCES crew (id),
                FOREIGN KEY (schedule_id) REFERENCES schedules (id)
            )
            """
        ]

        for table_sql in tables_to_create:
            cursor.execute(table_sql)
        print("✅ Database tables created/verified")

        # Add sample data if database is empty
        cursor.execute("SELECT COUNT(*) FROM buses")
        bus_count = cursor.fetchone()[0]

        if bus_count == 0:
            print("🔧 Adding sample data...")

            # Sample routes
            cursor.executemany("""
                INSERT INTO routes (route_name, start_point, end_point, distance, stops)
                VALUES (?, ?, ?, ?, ?)
            """, [
                ('Downtown Express', 'Central Station', 'Airport', 25.5, 'Main St, 5th Ave, Airport Rd'),
                ('City Circular', 'Bus Terminal', 'Bus Terminal', 15.0, 'All major city stops')
            ])

            # Sample crew
            cursor.executemany("""
                INSERT INTO crew (crew_id, name, role, contact_info, hire_date)
                VALUES (?, ?, ?, ?, ?)
            """, [
                ('DRV001', 'John Smith', 'Driver', '555-0101', '2023-01-15'),
                ('DRV002', 'Sarah Johnson', 'Driver', '555-0102', '2023-02-20')
            ])

            # Sample buses with GPS
            cursor.executemany("""
                INSERT INTO buses (registration_number, capacity, model, status, purchase_date, location_lat, location_lng, last_location_update)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, [
                ('BUS001', 45, 'Mercedes Citaro', 'active', '2023-01-01', 40.7128, -74.0060, datetime.now()),
                ('BUS002', 50, 'Volvo 7900', 'active', '2023-02-15', 40.7589, -73.9851, datetime.now())
            ])

            # Sample schedules
            cursor.executemany("""
                INSERT INTO schedules (route_id, bus_id, departure_time, arrival_time, frequency, active)
                VALUES (?, ?, ?, ?, ?, ?)
            """, [
                (1, 1, '08:00:00', '17:00:00', 'daily', 1),
                (2, 2, '09:00:00', '18:00:00', 'daily', 1)
            ])

            # Sample crew assignments
            cursor.executemany("""
                INSERT INTO crew_assignments (schedule_id, crew_id, assignment_date, notes)
                VALUES (?, ?, ?, ?)
            """, [
                (1, 1, '2025-01-01', 'Morning shift'),
                (2, 2, '2025-01-01', 'Morning shift')
            ])

            print("✅ Sample data added successfully")

        # Update active buses with GPS coordinates if they don't have them
        cursor.execute("""
            UPDATE buses
            SET location_lat = 40.7128 + (RANDOM() % 1000 - 500) * 0.0001,
                location_lng = -74.0060 + (RANDOM() % 1000 - 500) * 0.0001,
                last_location_update = datetime('now')
            WHERE status = 'active' AND (location_lat IS NULL OR location_lng IS NULL)
        """)

        updated = cursor.rowcount
        if updated > 0:
            print(f"✅ Added GPS coordinates to {updated} active buses")

        conn.commit()
        conn.close()

        print(f"\n🎉 SUCCESS! SQLAlchemy database fixed: {sqlalchemy_db_path}")
        return True

    except Exception as e:
        print(f"❌ Error fixing database: {e}")
        return False

def test_fix():
    """Test that the fix worked"""

    try:
        # Import and test Flask app
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from app import create_app

        app = create_app()
        with app.app_context():
            from app.models import db, Bus

            bus_count = Bus.query.count()
            print(f"✅ Test successful! Found {bus_count} buses in SQLAlchemy database")

            # Test the exact query that was failing
            active_buses = db.session.query(Bus).filter_by(status='active').all()
            print(f"✅ Query test successful! Found {len(active_buses)} active buses")

            if active_buses:
                bus = active_buses[0]
                print(f"✅ Sample bus: {bus.registration_number} with GPS: ({bus.location_lat}, {bus.location_lng})")

        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def main():
    print("=" * 60)
    print("🔧 FIXING SQLALCHEMY DATABASE ISSUE")
    print("=" * 60)

    # Find which database SQLAlchemy is using
    sqlalchemy_db_path = find_sqlalchemy_database()

    # Fix the database
    if fix_sqlalchemy_database(sqlalchemy_db_path):
        # Test the fix
        if test_fix():
            print("\n🎉 ALL TESTS PASSED!")
            print("\n🚀 Your Flask app should now work perfectly!")
            print("\nTo start the application:")
            print("   python run.py")
            print("\nThen visit the map dashboard:")
            print("   http://localhost:5000/dashboard/map")
        else:
            print("\n❌ Fix verification failed")

    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()