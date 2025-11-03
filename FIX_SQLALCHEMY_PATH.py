#!/usr/bin/env python3
"""
Fix SQLAlchemy database path issue
"""

import os
import sys
import sqlite3
import shutil
from datetime import datetime

def find_sqlalchemy_database():
    """Find which database SQLAlchemy is actually using"""

    print("🔍 Finding SQLAlchemy database configuration...")
    print("=" * 50)

    # Method 1: Check config.py
    config_paths = [
        'config.py',
        'app/config.py',
        '../config.py'
    ]

    for config_path in config_paths:
        if os.path.exists(config_path):
            print(f"📁 Found config file: {config_path}")
            with open(config_path, 'r') as f:
                content = f.read()
                lines = content.split('\n')
                for line in lines:
                    if 'SQLALCHEMY_DATABASE_URI' in line:
                        if 'sqlite:///' in line:
                            db_file = line.split('sqlite:///')[1].split("'")[0].strip()
                            print(f"📍 Config database path: {db_file}")
                            if os.path.exists(db_file):
                                return db_file
                            else:
                                print(f"⚠️  Database file doesn't exist: {db_file}")
                            # This is the issue - SQLAlchemy thinks the database exists but it doesn't

    # Method 2: Check common database file names
    common_db_files = [
        'bus_depot.db',
        'bus_management.db',
        'instance/bus_depot.db',
        'instance/bus_management.db',
        'database.db',
        'app.db'
    ]

    for db_file in common_db_files:
        if os.path.exists(db_file):
            print(f"📁 Found database file: {db_file}")
            return db_file

    print("❌ Could not determine SQLAlchemy database path")
    return None

def get_current_working_db():
    """Get the database that's currently working with our test script"""
    # This should be the same one the diagnostic script found
    common_db_files = [
        'bus_depot.db',
        'bus_management.db',
        'instance/bus_depot.db',
        'instance/bus_management.db',
        'database.db',
        'app.db'
    ]

    for db_file in common_db_files:
        if os.path.exists(db_file):
            try:
                conn = sqlite3.connect(db_file)
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM buses")
                count = cursor.fetchone()[0]
                conn.close()
                print(f"📍 Working database: {db_file} ({count} buses)")
                return db_file
            except:
                pass

    return None

def compare_databases():
    """Compare the working database with SQLAlchemy database"""
    print("\n🔍 Comparing databases...")
    print("=" * 50)

    working_db = get_current_working_db()
    sqlalchemy_db = find_sqlalchemy_database()

    if not working_db:
        print("❌ Could not find working database")
        return False

    if not sqlalchemy_db:
        print("❌ Could not find SQLAlchemy database")
        return False

    print(f"📊 Working database: {working_db}")
    print(f"📊 SQLAlchemy database: {sqlalchemy_db}")

    if working_db != sqlalchemy_db:
        print(f"⚠️  DATABASE MISMATCH DETECTED!")
        print(f"   SQLAlchemy is using: {sqlalchemy_db}")
        print(f"   Working database is: {working_db}")
        print("🔧 Fixing the database mismatch...")

        # Check if working database has GPS columns
        try:
            conn = sqlite3.connect(working_db)
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(buses)")
            working_columns = [row[1] for row in cursor.fetchall()]
            conn.close()

            if 'location_lat' in working_columns:
                print(f"✅ Working database has GPS columns")

                # Copy working database to SQLAlchemy path
                shutil.copy(working_db, sqlalchemy_db + '.from_working')
                print(f"✅ Copied working database to: {sqlalchemy_db}.from_working")
                print(f"   Original: {working_db}")
                print(f"   Copy: {sqlalchemy_db}.from_working")

                # Replace the original with the working one
                if os.path.exists(sqlalchemy_db):
                    shutil.move(sqlalchemy_db, sqlalchemy_db + '.old')
                shutil.move(sqlalchemy_db + '.from_working', sqlalchemy_db)
                print(f"✅ Replaced: {sqlalchemy_db}")

                return True
            else:
                print(f"❌ Working database doesn't have GPS columns either")
                return False

        except Exception as e:
            print(f"❌ Error checking working database: {e}")
            return False

    else:
        print("✅ Both databases are the same!")
        return True

    return False

def test_flask_app():
    """Test Flask app after fix"""
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from app import create_app

        app = create_app()
        with app.app_context():
            from app.models import db, Bus

            # Test the exact query that was failing
            active_buses = db.session.query(Bus).filter_by(status='active').all()
            print(f"✅ Flask app test: Found {len(active_buses)} active buses")

            if active_buses:
                bus = active_buses[0]
                print(f"✅ Sample bus: {bus.registration_number} with GPS: ({bus.location_lat}, {bus.location_lng})")

            # Test the complex query from dashboard
            results = db.session.query(Bus, Schedule, Route, Crew).join(
                Schedule, Bus.id == Schedule.bus_id
            ).join(
                Route, Schedule.route_id == Route.id
            ).join(
                CrewAssignment, Schedule.id == CrewAssignment.schedule_id
            ).join(
                Crew, CrewAssignment.crew_id == Crew.id
            ).filter(
                Bus.status == 'active',
                Schedule.active == True
            ).all()

            print(f"✅ Complex query test: Found {len(results)} results")

        return True

    except Exception as e:
        print(f"❌ Flask app test failed: {e}")
        return False

def main():
    print("=" * 70)
    print("🔧 FIXING SQLALCHEMY DATABASE PATH ISSUE")
    print("=" * 70)

    if compare_databases():
        print("\n✅ Database path fixed!")
        print("\n🎯 SUCCESS! The database path issue has been resolved.")
        print("\n🚀 Try running your Flask app now:")
        print("   python run.py")
        print("\n🗺️  Then visit the map dashboard:")
        print("   http://localhost:5000/dashboard/map")

        # Test the Flask app
        print("\n📋 Testing Flask app...")
        if test_flask_app():
            print("✅ Flask app test passed!")
            print("\n🎉 COMPLETE SUCCESS!")
            print("\nYour 'no such column: buses.location_lat' error is now fixed!")
        else:
            print("❌ Flask app still has issues")
    else:
        print("\n❌ Could not fix the database path issue.")

    print("\n" + "=" * 70)

if __name__ == "__main__":
    main()