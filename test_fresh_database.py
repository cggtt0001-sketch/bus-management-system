"""
Test database migration with a fresh database (simulating a new user)
"""

import os
import sqlite3
import shutil
from datetime import datetime

def backup_existing_database():
    """Backup existing database if it exists"""
    if os.path.exists('bus_depot.db'):
        shutil.copy('bus_depot.db', 'bus_depot_backup.db')
        print("✅ Backed up existing database")
        return True
    return False

def create_basic_database():
    """Create a basic database without GPS columns (simulating old database)"""
    conn = sqlite3.connect('bus_depot.db')
    cursor = conn.cursor()

    # Create basic buses table WITHOUT GPS columns
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

    # Create other basic tables
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

    # Add basic sample data
    cursor.executemany("""
        INSERT INTO routes (route_name, start_point, end_point, distance, stops)
        VALUES (?, ?, ?, ?, ?)
    """, [
        ('Downtown Express', 'Central Station', 'Airport', 25.5, 'Main St, 5th Ave, Airport Rd'),
        ('City Circular', 'Bus Terminal', 'Bus Terminal', 15.0, 'All major city stops')
    ])

    cursor.executemany("""
        INSERT INTO crew (crew_id, name, role, contact_info, hire_date)
        VALUES (?, ?, ?, ?, ?)
    """, [
        ('DRV001', 'John Smith', 'Driver', '555-0101', '2023-01-15'),
        ('DRV002', 'Sarah Johnson', 'Driver', '555-0102', '2023-02-20')
    ])

    cursor.executemany("""
        INSERT INTO buses (registration_number, capacity, model, status, purchase_date)
        VALUES (?, ?, ?, ?, ?)
    """, [
        ('BUS001', 45, 'Mercedes Citaro', 'active', '2023-01-01'),
        ('BUS002', 50, 'Volvo 7900', 'active', '2023-02-15')
    ])

    cursor.executemany("""
        INSERT INTO schedules (route_id, bus_id, departure_time, arrival_time, frequency, active)
        VALUES (?, ?, ?, ?, ?, ?)
    """, [
        (1, 1, '08:00:00', '17:00:00', 'daily', 1),
        (2, 2, '09:00:00', '18:00:00', 'daily', 1)
    ])

    cursor.executemany("""
        INSERT INTO crew_assignments (schedule_id, crew_id, assignment_date, notes)
        VALUES (?, ?, ?, ?)
    """, [
        (1, 1, '2025-01-01', 'Morning shift'),
        (2, 2, '2025-01-01', 'Morning shift')
    ])

    conn.commit()
    conn.close()

def test_migration():
    """Test the migration process"""
    print("🧪 Testing Database Migration Process...")
    print("=" * 60)

    # Step 1: Create basic database (simulating old database)
    print("📋 Step 1: Creating basic database (without GPS columns)...")
    create_basic_database()
    print("✅ Basic database created")

    # Step 2: Verify the database lacks GPS columns
    print("\n📋 Step 2: Verifying database lacks GPS columns...")
    conn = sqlite3.connect('bus_depot.db')
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(buses)")
    columns = [row[1] for row in cursor.fetchall()]
    conn.close()

    missing_columns = [col for col in ['location_lat', 'location_lng', 'last_location_update'] if col not in columns]
    if missing_columns:
        print(f"✅ Confirmed missing columns: {', '.join(missing_columns)}")
    else:
        print("❌ Database already has GPS columns")
        return False

    # Step 3: Run migration
    print("\n📋 Step 3: Running migration script...")
    import subprocess
    import sys
    result = subprocess.run([sys.executable, 'migrate_database.py'],
                          capture_output=True, text=True)

    if result.returncode == 0:
        print("✅ Migration script executed successfully")
        print("Output:", result.stdout)
    else:
        print("❌ Migration script failed")
        print("Error:", result.stderr)
        return False

    # Step 4: Verify migration worked
    print("\n📋 Step 4: Verifying migration results...")
    conn = sqlite3.connect('bus_depot.db')
    cursor = conn.cursor()

    # Check columns exist
    cursor.execute("PRAGMA table_info(buses)")
    columns = [row[1] for row in cursor.fetchall()]
    required_columns = ['location_lat', 'location_lng', 'last_location_update']

    all_columns_present = all(col in columns for col in required_columns)
    if all_columns_present:
        print("✅ All required GPS columns are now present")
    else:
        missing = [col for col in required_columns if col not in columns]
        print(f"❌ Still missing columns: {missing}")
        return False

    # Check working_hours table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='working_hours'")
    if cursor.fetchone():
        print("✅ Working hours table created")
    else:
        print("❌ Working hours table not found")
        return False

    # Check data integrity
    cursor.execute("SELECT COUNT(*) FROM buses WHERE status='active' AND location_lat IS NOT NULL")
    gps_buses = cursor.fetchone()[0]

    if gps_buses > 0:
        print(f"✅ {gps_buses} active buses now have GPS coordinates")
    else:
        print("⚠️  No active buses have GPS coordinates (but columns exist)")

    conn.close()
    return True

def test_flask_app_startup():
    """Test that Flask app can start with the migrated database"""
    print("\n📋 Step 5: Testing Flask app startup...")

    try:
        # Import and test Flask app initialization
        import sys
        sys.path.insert(0, os.path.dirname(__file__))

        from app import create_app
        app = create_app()

        print("✅ Flask app created successfully")

        # Test a simple database query through the app
        with app.app_context():
            from app.models import db, Bus
            bus_count = Bus.query.count()
            print(f"✅ Database connection works through Flask app ({bus_count} buses)")

        return True

    except Exception as e:
        print(f"❌ Flask app startup failed: {e}")
        return False

def restore_backup():
    """Restore the original database if it was backed up"""
    if os.path.exists('bus_depot_backup.db'):
        shutil.move('bus_depot_backup.db', 'bus_depot.db')
        print("✅ Restored original database")

def main():
    """Run the complete migration test"""
    print("=" * 70)
    print("🧪 Fresh Database Migration Test")
    print("=" * 70)

    # Backup existing database
    backed_up = backup_existing_database()

    try:
        # Test the migration process
        if test_migration():
            print("\n✅ Migration test passed!")

            # Test Flask app startup
            if test_flask_app_startup():
                print("\n✅ Flask app startup test passed!")
                print("\n🎉 COMPLETE SUCCESS!")
                print("✅ Database migration works for fresh databases")
                print("✅ Flask app can start and work with migrated database")
                print("✅ Map dashboard should load without errors")
            else:
                print("\n❌ Flask app startup test failed")
                return False
        else:
            print("\n❌ Migration test failed")
            return False

    finally:
        # Restore backup
        if backed_up:
            restore_backup()

    print("\n" + "=" * 70)
    return True

if __name__ == "__main__":
    main()