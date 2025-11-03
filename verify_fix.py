#!/usr/bin/env python3
"""
Simple verification script to test if the database issue is fixed
"""

import sqlite3
import os
import sys

def test_database_schema():
    """Test if the database has the required columns"""
    print("🔍 Testing Database Schema...")
    print("-" * 40)

    db_path = 'bus_depot.db'

    if not os.path.exists(db_path):
        print("❌ Database file not found!")
        return False

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Get column names from buses table
        cursor.execute("PRAGMA table_info(buses)")
        columns = [row[1] for row in cursor.fetchall()]

        print("📊 Current columns in buses table:")
        for col in columns:
            print(f"   - {col}")

        # Check for required GPS columns
        required = ['location_lat', 'location_lng', 'last_location_update']
        missing = [col for col in required if col not in columns]

        if missing:
            print(f"\n❌ MISSING COLUMNS: {missing}")
            print("This is what causes the 'no such column' error!")
            return False
        else:
            print(f"\n✅ All required columns present: {required}")

        # Test the exact query that was failing
        print("\n🔍 Testing the exact query that was failing...")
        try:
            query = """
            SELECT b.id, b.registration_number, b.location_lat, b.location_lng, b.status
            FROM buses b
            JOIN schedules s ON b.id = s.bus_id
            JOIN routes r ON s.route_id = r.id
            JOIN crew_assignments ca ON s.id = ca.schedule_id
            JOIN crew c ON ca.crew_id = c.id
            WHERE b.status = 'active' AND s.active = 1
            """

            cursor.execute(query)
            results = cursor.fetchall()
            print(f"✅ Query successful! Found {len(results)} active buses")

            if results:
                print("\n📍 Sample data:")
                for i, row in enumerate(results[:3]):
                    bus_id, reg_num, lat, lng, status = row
                    print(f"   {i+1}. {reg_num}: GPS({lat}, {lng}) - Status: {status}")

        except sqlite3.Error as e:
            print(f"❌ Query failed: {e}")
            return False

        conn.close()
        return True

    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def main():
    print("=" * 50)
    print("🗺️  Database Fix Verification")
    print("=" * 50)

    if test_database_schema():
        print("\n🎉 SUCCESS! The database issue appears to be fixed.")
        print("\n🚀 You can now try running the Flask app:")
        print("   python run.py")
        print("\n🗺️  And access the map at:")
        print("   http://localhost:5000/dashboard/map")
    else:
        print("\n❌ The database issue is NOT fixed.")
        print("\n🔧 Please run the fix command:")
        print("   python migrate_database.py")
        print("\nThen try this test again.")

if __name__ == "__main__":
    main()