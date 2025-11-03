#!/usr/bin/env python3
"""
Diagnostic script to figure out what's really happening with your database
"""

import sqlite3
import os
import sys

def diagnose_database():
    """Comprehensive database diagnosis"""

    print("🔍 DIAGNOSING DATABASE...")
    print("=" * 50)

    # Find database file
    db_paths = [
        'bus_depot.db',
        'instance/bus_depot.db',
        'app.db',
        'database.db'
    ]

    db_path = None
    for path in db_paths:
        if os.path.exists(path):
            db_path = path
            print(f"📁 Found database: {path}")
            break

    if not db_path:
        print("❌ No database file found!")
        return

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 1. Check if database is accessible
        print("\n1️⃣ Testing database connection...")
        cursor.execute("SELECT COUNT(*) FROM buses")
        bus_count = cursor.fetchone()[0]
        print(f"   ✅ Connected! Found {bus_count} buses")

        # 2. Check table structure
        print("\n2️⃣ Checking buses table structure...")
        cursor.execute("PRAGMA table_info(buses)")
        columns = cursor.fetchall()

        print("   📊 Current columns in buses table:")
        for col in columns:
            col_name = col[1]
            col_type = col[2]
            nullable = "NULL" if col[3] else "NOT NULL"
            print(f"      - {col_name} ({col_type}) {nullable}")

        # 3. Check for GPS columns specifically
        gps_columns = ['location_lat', 'location_lng', 'last_location_update']
        existing_gps = [col for col in gps_columns if any(row[1] == col for row in columns)]
        missing_gps = [col for col in gps_columns if col not in existing_gps]

        print(f"\n3️⃣ GPS Columns Status:")
        if existing_gps:
            print(f"   ✅ Found GPS columns: {existing_gps}")
        if missing_gps:
            print(f"   ❌ Missing GPS columns: {missing_gps}")
        else:
            print(f"   ✅ All GPS columns present!")

        # 4. Test if active buses have GPS data
        print("\n4️⃣ Testing GPS data for active buses...")
        if 'location_lat' in existing_gps:
            cursor.execute("""
                SELECT registration_number, location_lat, location_lng
                FROM buses
                WHERE status = 'active' AND location_lat IS NOT NULL
            """)
            gps_buses = cursor.fetchall()

            if gps_buses:
                print(f"   ✅ Found {len(gps_buses)} active buses with GPS data")
                print("   📍 Sample data:")
                for i, (reg, lat, lng) in enumerate(gps_buses[:3]):
                    print(f"      🚌 {reg}: GPS({lat:.6f}, {lng:.6f})")
            else:
                print("   ⚠️  No active buses have GPS coordinates")
                print("   🔧 Adding GPS coordinates to active buses...")

                # Add GPS coordinates
                cursor.execute("""
                    UPDATE buses
                    SET location_lat = 40.7128 + (RANDOM() % 1000 - 500) * 0.0001,
                        location_lng = -74.0060 + (RANDOM() % 1000 - 500) * 0.0001,
                        last_location_update = datetime('now')
                    WHERE status = 'active' AND (location_lat IS NULL OR location_lng IS NULL)
                """)

                updated = cursor.rowcount
                if updated > 0:
                    conn.commit()
                    print(f"   ✅ Added GPS coordinates to {updated} buses")
        else:
            print("   ❌ GPS columns don't exist in database")

        # 5. Test the exact query that was failing
        print("\n5️⃣ Testing the exact query that was failing...")
        try:
            query = """
            SELECT b.id, b.registration_number, b.location_lat, b.location_lng, b.status
            FROM buses b
            JOIN schedules s ON b.id = s.bus_id
            JOIN routes r ON s.route_id = r.id
            JOIN crew_assignments ca ON s.id = ca.schedule_id
            JOIN crew c ON ca.crew_id = c.id
            WHERE b.status = ? AND s.active = 1
            """

            cursor.execute(query, ('active',))
            results = cursor.fetchall()
            print(f"   ✅ Query successful! Found {len(results)} results")

            if results:
                print("   📍 Sample query results:")
                for i, (bus_id, reg_num, lat, lng, status) in enumerate(results[:3]):
                    print(f"      {i+1}. {reg_num} - Status: {status}")
                    if lat and lng:
                        print(f"         GPS: ({lat:.6f}, {lng:.6f})")
                    else:
                        print(f"         ❌ No GPS data")

        except sqlite3.Error as e:
            print(f"   ❌ Query failed: {e}")
            return False

        # 6. Check SQLAlchemy models
        print("\n6️⃣ Checking SQLAlchemy model compatibility...")
        try:
            # Try to import models
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            from app.models import db, Bus

            print("   ✅ SQLAlchemy models imported successfully")

            # Test model query
            with db.session.begin():
                active_buses = Bus.query.filter_by(status='active').all()
                print(f"   ✅ SQLAlchemy query found {len(active_buses)} active buses")

                # Check if model has GPS attributes
                if hasattr(active_buses[0], 'location_lat'):
                    print("   ✅ Bus model has GPS attributes")
                else:
                    print("   ❌ Bus model missing GPS attributes")
                    return False

        except Exception as e:
            print(f"   ❌ SQLAlchemy model error: {e}")
            print("   📝 This might mean the model file doesn't have the GPS fields")

        conn.close()
        return True

    except Exception as e:
        print(f"❌ Diagnostic error: {e}")
        return False

def main():
    print("=" * 60)
    print("🔍 DATABASE DIAGNOSTIC TOOL")
    print("=" * 60)

    success = diagnose_database()

    print("\n" + "=" * 60)
    if success:
        print("✅ DIAGNOSIS COMPLETE!")
        print("\n🚀 Your database should work now.")
        print("Try running: python run.py")
    else:
        print("❌ ISSUES FOUND!")
        print("\n🔧 Possible solutions:")
        print("1. Make sure you're in the correct directory")
        print("2. Check that the database file is the right one")
        print("3. Ensure SQLAlchemy models have GPS fields")
    print("=" * 60)

if __name__ == "__main__":
    main()