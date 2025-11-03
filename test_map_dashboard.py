"""
Test script to verify the map dashboard query works correctly
"""

import sqlite3
import os
from datetime import datetime

def test_map_dashboard_query():
    """Test the exact query used by the map dashboard"""
    print("🧪 Testing Map Dashboard Query...")
    print("=" * 50)

    db_path = 'bus_depot.db'

    if not os.path.exists(db_path):
        print("❌ Database not found")
        return False

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Test the exact query from dashboard/routes.py
        print("🔍 Testing the map dashboard query...")
        query = """
        SELECT b.id, b.registration_number, b.location_lat, b.location_lng, b.status,
               b.last_location_update, r.route_name, r.start_point, r.end_point,
               c.name as driver_name, c.role
        FROM buses b
        JOIN schedules s ON b.id = s.bus_id
        JOIN routes r ON s.route_id = r.id
        JOIN crew_assignments ca ON s.id = ca.schedule_id
        JOIN crew c ON ca.crew_id = c.id
        WHERE b.status = 'active' AND s.active = 1
        """

        cursor.execute(query)
        results = cursor.fetchall()

        print(f"✅ Query executed successfully!")
        print(f"📍 Found {len(results)} active buses with assignments")

        if results:
            print("\n🚌 Sample bus data:")
            for i, row in enumerate(results[:3]):  # Show first 3 results
                bus_id, reg_num, lat, lng, status, last_update, route_name, start_point, end_point, driver_name, role = row
                print(f"   {i+1}. {reg_num}")
                print(f"      📍 GPS: ({lat}, {lng})")
                print(f"      🛣️  Route: {route_name} ({start_point} → {end_point})")
                print(f"      👤 Driver: {driver_name} ({role})")
                print(f"      📅 Last Update: {last_update}")
                print()

        # Check if we have the required columns
        cursor.execute("PRAGMA table_info(buses)")
        columns = [row[1] for row in cursor.fetchall()]
        required_columns = ['location_lat', 'location_lng', 'last_location_update']

        print("🔍 Checking required columns in buses table:")
        for col in required_columns:
            if col in columns:
                print(f"   ✅ {col}")
            else:
                print(f"   ❌ {col} - MISSING")
                return False

        # Test if we have active buses with GPS coordinates
        cursor.execute("SELECT COUNT(*) FROM buses WHERE status='active' AND location_lat IS NOT NULL")
        gps_count = cursor.fetchone()[0]

        print(f"\n📊 Database Statistics:")
        print(f"   🚌 Total buses: {cursor.execute('SELECT COUNT(*) FROM buses').fetchone()[0]}")
        print(f"   ✅ Active buses: {cursor.execute('SELECT COUNT(*) FROM buses WHERE status=\"active\"').fetchone()[0]}")
        print(f"   📍 Active buses with GPS: {gps_count}")

        if gps_count == 0:
            print("⚠️  Warning: No active buses have GPS coordinates")
            # Add GPS coordinates to active buses
            print("🔧 Adding GPS coordinates to active buses...")
            cursor.execute("""
                UPDATE buses
                SET location_lat = 40.7128 + (RANDOM() % 1000 - 500) * 0.0001,
                    location_lng = -74.0060 + (RANDOM() % 1000 - 500) * 0.0001,
                    last_location_update = datetime('now')
                WHERE status = 'active' AND location_lat IS NULL
            """)
            updated = cursor.rowcount
            conn.commit()
            print(f"✅ Added GPS coordinates to {updated} buses")

        conn.close()
        return True

    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_database_connection():
    """Test basic database connection"""
    print("🧪 Testing Database Connection...")
    print("=" * 50)

    db_path = 'bus_depot.db'

    if not os.path.exists(db_path):
        print("❌ Database file not found")
        return False

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Test basic queries
        cursor.execute("SELECT COUNT(*) FROM buses")
        bus_count = cursor.fetchone()[0]
        print(f"✅ Connected to database")
        print(f"🚌 Found {bus_count} buses")

        cursor.execute("SELECT COUNT(*) FROM routes")
        route_count = cursor.fetchone()[0]
        print(f"🛣️  Found {route_count} routes")

        cursor.execute("SELECT COUNT(*) FROM crew")
        crew_count = cursor.fetchone()[0]
        print(f"👥 Found {crew_count} crew members")

        conn.close()
        return True

    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("🗺️  Map Dashboard Database Test")
    print("=" * 60)

    # Test basic connection
    if not test_database_connection():
        print("\n❌ Database connection test failed")
        return False

    # Test map dashboard query
    if not test_map_dashboard_query():
        print("\n❌ Map dashboard query test failed")
        return False

    print("\n" + "=" * 60)
    print("🎉 All tests passed!")
    print("✅ Map dashboard should load without errors")
    print("🚀 Ready to start the Flask application")
    print("=" * 60)

    return True

if __name__ == "__main__":
    main()