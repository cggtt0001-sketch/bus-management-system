#!/usr/bin/env python3
<arg_value>Simple script to add missing GPS columns to existing database
"""

import sqlite3
import os
from datetime import datetime

def add_gps_columns():
    """Add missing GPS columns to existing database"""

    print("🔧 Adding GPS columns to existing database...")
    print("=" * 50)

    db_path = 'bus_management.db'

    if not os.path.exists(db_path):
        print("❌ Database file not found!")
        print("🔧 Please run: python CREATE_COMPLETE_DATABASE.py")
        return False

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check current columns
        cursor.execute("PRAGMA table_info(buses)")
        columns = [row[1] for row in cursor.fetchall()]
        print(f"📊 Current columns: {columns}")

        # Check which GPS columns are missing
        required_columns = ['location_lat', 'location_lng', 'last_location_update']
        missing_columns = [col for col in required_columns if col not in columns]

        if not missing_columns:
            print("✅ All GPS columns already exist!")
            return True

        print(f"🔧 Adding missing columns: {missing_columns}")

        # Add missing columns
        for col in missing_columns:
            try:
                if col == 'location_lat':
                    cursor.execute("ALTER TABLE buses ADD COLUMN location_lat REAL")
                    print("   ✅ Added location_lat")
                elif col == 'location_lng':
                    cursor.execute("ALTER TABLE buses ADD COLUMN location_lng REAL")
                    print("   ✅ Added location_lng")
                elif col == 'last_location_update':
                    cursor.execute("ALTER TABLE buses ADD COLUMN last_location_update DATETIME")
                    print("   ✅ Added last_location_update")
            except sqlite3.Error as e:
                if "duplicate column name" in str(e):
                    print(f"   ⚠️  Column {col} already exists")
                else:
                    print(f"   ❌ Error adding {col}: {e}")
                    return False

        conn.commit()
        print(f"✅ Added {len(missing_columns)} missing columns successfully")

        # Check if we need to create other tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        existing_tables = [row[0] for row in cursor.fetchall()]
        required_tables = ['routes', 'crew', 'schedules', 'crew_assignments', 'working_hours']
        missing_tables = [table for table in required_tables if table not in existing_tables]

        if missing_tables:
            print(f"🔧 Creating missing tables: {missing_tables}")

            if 'routes' in missing_tables:
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

            if 'crew' in missing_tables:
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

            if 'schedules' in missing_tables:
                cursor.execute("""
                    CREATE TABLE schedules (
                        id INTEGER KEY PRIMARY KEY AUTOINCREMENT,
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

            if 'crew_assignments' in missing_tables:
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

            if 'working_hours' in missing_tables:
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

            conn.commit()

        # Add GPS coordinates to active buses that don't have them
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
        else:
            print("✅ All active buses already have GPS coordinates")

        conn.close()
        return True

    except Exception as e:
        print(f"❌ Error adding GPS columns: {e}")
        return False

def test_fix():
    """Test that the fix worked"""

    print("\n🔍 Testing the fix...")
    print("=" * 30)

    try:
        conn = sqlite3.connect('bus_management.db')
        cursor = conn.cursor()

        # Test the exact query that was failing
        query = """
        SELECT b.id, b.registration_number, b.location_lat, b.location_lng, b.status
        FROM buses b
        WHERE b.status = 'active'
        """

        cursor.execute(query)
        results = cursor.fetchall()

        print(f"✅ Query successful! Found {len(results)} active buses")

        if results:
            for i, (bus_id, reg_num, lat, lng, status) in enumerate(results):
                print(f"   🚌 {reg_num}: GPS({lat}, {lng}) - {status}")

        conn.close()
        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def main():
    print("=" * 60)
    print("🔧 ADDING GPS COLUMNS TO EXISTING DATABASE")
    print("=" * 60)

    if add_gps_columns():
        if test_fix():
            print("\n✅ SUCCESS! GPS columns added successfully!")
            print("\n🚀 Try running your Flask app now:")
            print("   python run.py")
            print("\n🗺️  Then visit the map dashboard:")
            print("   http://localhost:5000/dashboard/map")
        else:
            print("\n❌ Failed to add GPS columns!")

    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()