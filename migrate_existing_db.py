"""
Database migration script for existing databases
Adds the new location fields to the buses table and creates working_hours table
"""

import sqlite3
import os
from datetime import datetime
import random

def check_database_exists():
    """Check if database exists and show current state"""
    db_files = ['bus_depot.db', 'instance/bus_depot.db', 'app.db']

    for db_file in db_files:
        if os.path.exists(db_file):
            print(f"Found database: {db_file}")
            return db_file

    print("No existing database found. Creating new one...")
    return None

def migrate_database(db_path):
    """Migrate existing database to add new fields"""

    if not db_path:
        # Create new database if none exists
        from setup_database import create_database
        create_database()
        return

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        print(f"Migrating database: {db_path}")

        # Check if location columns already exist
        cursor.execute("PRAGMA table_info(buses)")
        columns = [row[1] for row in cursor.fetchall()]

        # Add location columns if they don't exist
        if 'location_lat' not in columns:
            print("Adding location_lat column...")
            cursor.execute("ALTER TABLE buses ADD COLUMN location_lat REAL")
            print("✅ Added location_lat column")
        else:
            print("✅ location_lat column already exists")

        if 'location_lng' not in columns:
            print("Adding location_lng column...")
            cursor.execute("ALTER TABLE buses ADD COLUMN location_lng REAL")
            print("✅ Added location_lng column")
        else:
            print("✅ location_lng column already exists")

        if 'last_location_update' not in columns:
            print("Adding last_location_update column...")
            cursor.execute("ALTER TABLE buses ADD COLUMN last_location_update DATETIME")
            print("✅ Added last_location_update column")
        else:
            print("✅ last_location_update column already exists")

        # Check if working_hours table exists
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
            print("✅ Created working_hours table")

            # Add sample working hours data
            print("Adding sample working hours data...")
            cursor.execute("SELECT id FROM crew")
            crew_ids = [row[0] for row in cursor.fetchall()]

            sample_hours = []
            for crew_id in crew_ids:
                for day in range(1, 31):  # 30 days of sample data
                    hours = round(random.uniform(6, 10), 1)
                    sample_hours.append((crew_id, f'2025-01-{day:02d}', hours, None))

            cursor.executemany("INSERT INTO working_hours (crew_id, date, hours_worked, schedule_id) VALUES (?, ?, ?, ?)", sample_hours)
            print(f"✅ Added {len(sample_hours)} working hours records")
        else:
            print("✅ working_hours table already exists")

        # Update existing buses with mock coordinates if they don't have them
        cursor.execute("SELECT COUNT(*) FROM buses WHERE status='active' AND location_lat IS NULL")
        buses_to_update = cursor.fetchone()[0]

        if buses_to_update > 0:
            print(f"Updating {buses_to_update} active buses with mock coordinates...")
            cursor.execute("""
                UPDATE buses
                SET location_lat = 40.7128 + (RANDOM() % 1000 - 500) * 0.0001,
                    location_lng = -74.0060 + (RANDOM() % 1000 - 500) * 0.0001,
                    last_location_update = datetime('now')
                WHERE status = 'active' AND location_lat IS NULL
            """)
            updated = cursor.rowcount
            print(f"✅ Updated {updated} buses with GPS coordinates")
        else:
            print("✅ All active buses already have GPS coordinates")

        # Show final database state
        print("\n📊 Database State After Migration:")
        cursor.execute("SELECT COUNT(*) FROM buses")
        bus_count = cursor.fetchone()[0]
        print(f"   🚌 Total buses: {bus_count}")

        cursor.execute("SELECT COUNT(*) FROM buses WHERE status='active'")
        active_count = cursor.fetchone()[0]
        print(f"   ✅ Active buses: {active_count}")

        cursor.execute("SELECT COUNT(*) FROM buses WHERE location_lat IS NOT NULL")
        with_gps = cursor.fetchone()[0]
        print(f"   📍 Buses with GPS: {with_gps}")

        cursor.execute("SELECT COUNT(*) FROM working_hours")
        hours_count = cursor.fetchone()[0]
        print(f"   ⏰ Working hours records: {hours_count}")

        conn.commit()
        conn.close()

        print(f"\n🎉 Migration completed successfully!")
        print(f"📍 Database: {os.path.abspath(db_path)}")

    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        if conn:
            conn.rollback()
            conn.close()
        raise
    except Exception as e:
        print(f"❌ Migration error: {e}")
        if conn:
            conn.close()
        raise

if __name__ == "__main__":
    print("=" * 60)
    print("🚌 Bus Depot Management System - Database Migration")
    print("=" * 60)

    db_path = check_database_exists()
    migrate_database(db_path)

    print("\n" + "=" * 60)
    print("✅ Migration complete! You can now run the application.")
    print("🗺️  Live Map: http://localhost:5000/dashboard/map")
    print("=" * 60)