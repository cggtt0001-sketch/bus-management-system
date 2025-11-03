"""
Ensure active buses have GPS coordinates
"""

import sqlite3
import os
from datetime import datetime

def add_gps_coordinates():
    """Add GPS coordinates to active buses that don't have them"""
    db_path = 'bus_depot.db'

    if not os.path.exists(db_path):
        print("❌ Database not found")
        return False

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check for active buses without GPS
        cursor.execute("""
            SELECT id, registration_number FROM buses
            WHERE status = 'active' AND (location_lat IS NULL OR location_lng IS NULL)
        """)
        buses_to_update = cursor.fetchall()

        if not buses_to_update:
            print("✅ All active buses already have GPS coordinates")
            return True

        print(f"🔧 Adding GPS coordinates to {len(buses_to_update)} active buses...")

        # Mock GPS coordinates for New York area
        for bus_id, reg_num in buses_to_update:
            # Generate random coordinates around NYC
            import random
            lat = 40.7128 + (random.random() - 0.5) * 0.1
            lng = -74.0060 + (random.random() - 0.5) * 0.1

            cursor.execute("""
                UPDATE buses
                SET location_lat = ?, location_lng = ?, last_location_update = ?
                WHERE id = ?
            """, (lat, lng, datetime.now(), bus_id))

            print(f"   ✅ {reg_num}: GPS ({lat:.6f}, {lng:.6f})")

        conn.commit()
        conn.close()

        print(f"✅ Updated {len(buses_to_update)} buses with GPS coordinates")
        return True

    except Exception as e:
        print(f"❌ Error adding GPS coordinates: {e}")
        return False

def verify_gps_data():
    """Verify that we have active buses with GPS data"""
    try:
        conn = sqlite3.connect('bus_depot.db')
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM buses WHERE status='active' AND location_lat IS NOT NULL")
        count = cursor.fetchone()[0]

        if count > 0:
            print(f"✅ Found {count} active buses with GPS coordinates")

            # Show sample data
            cursor.execute("""
                SELECT registration_number, location_lat, location_lng, last_location_update
                FROM buses
                WHERE status='active' AND location_lat IS NOT NULL
                LIMIT 3
            """)

            results = cursor.fetchall()
            print("\n📍 Sample GPS Data:")
            for reg_num, lat, lng, last_update in results:
                print(f"   🚌 {reg_num}: ({lat:.6f}, {lng:.6f})")
                print(f"      📅 Last Update: {last_update}")
        else:
            print("❌ No active buses with GPS coordinates found")

        conn.close()
        return count > 0

    except Exception as e:
        print(f"❌ Error verifying GPS data: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("🗺️  Ensuring GPS Data for Active Buses")
    print("=" * 50)

    if add_gps_coordinates():
        verify_gps_data()
        print("\n✅ GPS data setup complete!")
        print("🗺️  Map dashboard should now show buses on the map")
    else:
        print("\n❌ Failed to set up GPS data")

    print("=" * 50)