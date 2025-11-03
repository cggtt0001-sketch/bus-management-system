"""
Automatic Database Migration Script
Ensures the database schema matches the SQLAlchemy models
"""

import os
import sqlite3
import sys
from datetime import datetime

def get_database_path():
    """Find the database file"""
    possible_paths = [
        'bus_depot.db',
        'instance/bus_depot.db',
        '../bus_depot.db',
        'app.db'
    ]

    for path in possible_paths:
        if os.path.exists(path):
            return path
    return 'bus_depot.db'  # Default path

def check_table_schema(db_path, table_name):
    """Get the current schema of a table"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        conn.close()
        return {row[1]: {'type': row[2], 'nullable': not row[3], 'default': row[4]} for row in columns}
    except Exception as e:
        print(f"Error checking schema for {table_name}: {e}")
        return {}

def create_database_if_needed(db_path):
    """Create a basic database if it doesn't exist"""
    if os.path.exists(db_path):
        return False

    print(f"Creating new database at: {db_path}")

    # Create directory if needed
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create basic tables
    cursor.execute("""
        CREATE TABLE buses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            registration_number VARCHAR(50) UNIQUE NOT NULL,
            capacity INTEGER NOT NULL,
            model VARCHAR(100),
            status VARCHAR(20) DEFAULT 'active',
            purchase_date DATE
        )
    """)

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

    conn.commit()
    conn.close()

    return True

def add_missing_columns(db_path):
    """Add missing GPS columns to the buses table"""
    print(f"Checking database schema at: {db_path}")

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Get current schema
        current_schema = check_table_schema(db_path, 'buses')

        # Define required columns
        required_columns = {
            'location_lat': 'REAL',
            'location_lng': 'REAL',
            'last_location_update': 'DATETIME'
        }

        columns_added = []

        for column_name, column_type in required_columns.items():
            if column_name not in current_schema:
                print(f"Adding column: {column_name} ({column_type})")
                cursor.execute(f"ALTER TABLE buses ADD COLUMN {column_name} {column_type}")
                columns_added.append(column_name)
            else:
                print(f"Column already exists: {column_name}")

        if columns_added:
            conn.commit()
            print(f"✅ Added {len(columns_added)} columns to buses table: {', '.join(columns_added)}")
        else:
            print("✅ All required columns already exist")

        # Also check if working_hours table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='working_hours'")
        if not cursor.fetchone():
            print("Creating working_hours table...")
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
            conn.commit()
            print("✅ Created working_hours table")
        else:
            print("✅ Working hours table already exists")

        conn.close()
        return True

    except Exception as e:
        print(f"❌ Error adding columns: {e}")
        if 'conn' in locals():
            conn.close()
        return False

def add_sample_data(db_path):
    """Add sample data if the database is empty"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check if buses table is empty
        cursor.execute("SELECT COUNT(*) FROM buses")
        bus_count = cursor.fetchone()[0]

        if bus_count == 0:
            print("Adding sample data...")

            # Sample routes
            cursor.executemany("""
                INSERT INTO routes (route_name, start_point, end_point, distance, stops)
                VALUES (?, ?, ?, ?, ?)
            """, [
                ('Downtown Express', 'Central Station', 'Airport', 25.5, 'Main St, 5th Ave, Airport Rd'),
                ('City Circular', 'Bus Terminal', 'Bus Terminal', 15.0, 'All major city stops'),
                ('University Route', 'Campus North', 'Downtown', 8.2, 'Campus areas, shopping district'),
                ('Suburban Connector', 'Suburb Mall', 'City Center', 12.8, 'Residential areas, office park')
            ])

            # Sample crew
            cursor.executemany("""
                INSERT INTO crew (crew_id, name, role, contact_info, hire_date)
                VALUES (?, ?, ?, ?, ?)
            """, [
                ('DRV001', 'John Smith', 'Driver', '555-0101', '2023-01-15'),
                ('DRV002', 'Sarah Johnson', 'Driver', '555-0102', '2023-02-20'),
                ('COND001', 'Mike Wilson', 'Conductor', '555-0103', '2023-03-10'),
                ('COND002', 'Emily Davis', 'Conductor', '555-0104', '2023-04-05')
            ])

            # Sample buses with GPS coordinates
            cursor.executemany("""
                INSERT INTO buses (registration_number, capacity, model, status, purchase_date, location_lat, location_lng, last_location_update)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, [
                ('BUS001', 45, 'Mercedes Citaro', 'active', '2023-01-01', 40.7128, -74.0060, datetime.now()),
                ('BUS002', 50, 'Volvo 7900', 'active', '2023-02-15', 40.7589, -73.9851, datetime.now()),
                ('BUS003', 40, 'MAN Lion\'s City', 'active', '2023-03-20', 40.7282, -73.9942, datetime.now())
            ])

            # Sample schedules
            cursor.executemany("""
                INSERT INTO schedules (route_id, bus_id, departure_time, arrival_time, frequency, active)
                VALUES (?, ?, ?, ?, ?, ?)
            """, [
                (1, 1, '08:00:00', '17:00:00', 'daily', 1),
                (2, 2, '09:00:00', '18:00:00', 'daily', 1),
                (3, 3, '07:30:00', '16:30:00', 'daily', 1)
            ])

            # Sample crew assignments
            cursor.executemany("""
                INSERT INTO crew_assignments (schedule_id, crew_id, assignment_date, notes)
                VALUES (?, ?, ?, ?)
            """, [
                (1, 1, '2025-01-01', 'Morning shift'),
                (1, 3, '2025-01-01', 'Morning shift'),
                (2, 2, '2025-01-01', 'Morning shift'),
                (2, 4, '2025-01-01', 'Morning shift'),
                (3, 1, '2025-01-01', 'Afternoon shift'),
                (3, 3, '2025-01-01', 'Afternoon shift')
            ])

            conn.commit()
            print("✅ Added sample data")
        else:
            print(f"✅ Database already has {bus_count} buses")

        conn.close()
        return True

    except Exception as e:
        print(f"❌ Error adding sample data: {e}")
        if 'conn' in locals():
            conn.close()
        return False

def main():
    """Main migration function"""
    print("=" * 60)
    print("🗺️  Database Migration for Bus GPS Tracking")
    print("=" * 60)

    # Get database path
    db_path = get_database_path()

    # Create database if needed
    if create_database_if_needed(db_path):
        print("✅ New database created")

    # Add missing columns
    if not add_missing_columns(db_path):
        print("❌ Failed to add missing columns")
        sys.exit(1)

    # Add sample data if needed
    if not add_sample_data(db_path):
        print("❌ Failed to add sample data")
        sys.exit(1)

    # Verify migration
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check that required columns exist
        cursor.execute("PRAGMA table_info(buses)")
        columns = [row[1] for row in cursor.fetchall()]
        required = ['location_lat', 'location_lng', 'last_location_update']

        missing = [col for col in required if col not in columns]
        if missing:
            print(f"❌ Missing columns after migration: {missing}")
            sys.exit(1)

        # Check that we have some active buses with GPS
        cursor.execute("SELECT COUNT(*) FROM buses WHERE status='active' AND location_lat IS NOT NULL")
        gps_buses = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM buses")
        total_buses = cursor.fetchone()[0]

        conn.close()

        print("=" * 60)
        print("🎉 Migration completed successfully!")
        print(f"📍 Database: {os.path.abspath(db_path)}")
        print(f"🚌 Total buses: {total_buses}")
        print(f"🗺️  Buses with GPS: {gps_buses}")
        print("=" * 60)

    except Exception as e:
        print(f"❌ Migration verification failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()