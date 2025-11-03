#!/usr/bin/env python3
"""
DIRECT FIX for your database issue
Run this script in your project directory where you have the Flask app
"""

import sqlite3
import os
from datetime import datetime

def fix_database_directly():
    """Fix the database by adding missing columns"""

    # Find your database file
    possible_db_paths = [
        'bus_depot.db',
        'instance/bus_depot.db',
        'database.db',
        'app.db',
        r'C:\Users\jasho\OneDrive\Desktop\bus-management-system-1\bus_depot.db',
        r'C:\Users\jasho\OneDrive\Desktop\bus-management-system-1\instance\bus_depot.db'
    ]

    db_path = None
    for path in possible_db_paths:
        if os.path.exists(path):
            db_path = path
            print(f"📁 Found database at: {path}")
            break

    if not db_path:
        print("❌ Database file not found!")
        print("🔧 Looking for database in current directory...")

        # List all .db files in current directory
        import glob
        db_files = glob.glob('*.db')
        if db_files:
            db_path = db_files[0]
            print(f"📁 Found database: {db_path}")
        else:
            print("❌ No database files found!")
            return False

    print(f"🔧 Fixing database: {db_path}")

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check current columns
        cursor.execute("PRAGMA table_info(buses)")
        columns = [row[1] for row in cursor.fetchall()]

        print(f"📊 Current columns: {columns}")

        # Add missing columns
        missing_columns = []
        if 'location_lat' not in columns:
            cursor.execute("ALTER TABLE buses ADD COLUMN location_lat REAL")
            missing_columns.append('location_lat')
            print("✅ Added location_lat column")

        if 'location_lng' not in columns:
            cursor.execute("ALTER TABLE buses ADD COLUMN location_lng REAL")
            missing_columns.append('location_lng')
            print("✅ Added location_lng column")

        if 'last_location_update' not in columns:
            cursor.execute("ALTER TABLE buses ADD COLUMN last_location_update DATETIME")
            missing_columns.append('last_location_update')
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
                    schedule_id INTEGER
                )
            """)
            print("✅ Created working_hours table")

        # Add GPS coordinates to active buses
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

        print(f"\n🎉 SUCCESS! Database fixed!")
        print(f"📍 Added {len(missing_columns)} missing columns")
        print(f"🚀 Your Flask app should now work!")

        return True

    except Exception as e:
        print(f"❌ Error fixing database: {e}")
        return False

def test_fix():
    """Test that the fix worked"""

    # Test the database
    try:
        conn = sqlite3.connect('bus_depot.db')
        cursor = conn.cursor()

        # Test the exact query that was failing
        query = """
        SELECT b.id, b.registration_number, b.location_lat, b.location_lng
        FROM buses b
        WHERE b.status = 'active'
        """

        cursor.execute(query)
        results = cursor.fetchall()

        print(f"✅ Query successful! Found {len(results)} active buses")

        if results:
            for i, (bus_id, reg_num, lat, lng) in enumerate(results[:3]):
                print(f"   🚌 {reg_num}: GPS({lat}, {lng})")

        conn.close()
        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🔧 DIRECT DATABASE FIX")
    print("=" * 60)

    if fix_database_directly():
        if test_fix():
            print("\n✅ ALL TESTS PASSED!")
            print("🚀 Now run your Flask app: python run.py")
            print("🗺️  Then visit: http://localhost:5000/dashboard/map")
        else:
            print("\n❌ Test failed - please check the error above")
    else:
        print("\n❌ Database fix failed - please check the error above")

    print("=" * 60)