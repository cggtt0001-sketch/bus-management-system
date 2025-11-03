#!/usr/bin/env python3
"""
Test Flask app startup and identify the exact issue
"""

import sys
import os

def test_flask_app():
    """Test the Flask app startup process"""

    print("🔍 TESTING FLASK APP STARTUP...")
    print("=" * 50)

    try:
        # Add current directory to path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)

        print("1️⃣ Importing Flask app...")
        from app import create_app
        print("   ✅ Flask app imported successfully")

        print("2️⃣ Creating Flask app instance...")
        app = create_app()
        print("   ✅ Flask app created successfully")

        print("3️⃣ Testing database connection within app context...")
        with app.app_context():
            from app.models import db, Bus

            # Test basic query
            bus_count = Bus.query.count()
            print(f"   ✅ Database connection works! Found {bus_count} buses")

            # Test specific query that was failing
            try:
                active_buses = Bus.query.filter_by(status='active').all()
                print(f"   ✅ Basic query works! Found {len(active_buses)} active buses")

                # Check if Bus model has GPS attributes
                if active_buses:
                    bus = active_buses[0]
                    has_gps = hasattr(bus, 'location_lat') and hasattr(bus, 'location_lng')
                    print(f"   ✅ Bus model GPS attributes: {'Present' if has_gps else 'Missing'}")

                    if has_gps:
                        lat = getattr(bus, 'location_lat', None)
                        lng = getattr(bus, 'location_lng', None)
                        print(f"   📍 Sample GPS data: ({lat}, {lng})")
                        if lat is None or lng is None:
                            print("   ⚠️  GPS columns exist but data is NULL")

            print("4️⃣ Testing the exact query from dashboard/routes.py...")
            try:
                from app.models import Bus, Route, Schedule, Crew, CrewAssignment

                # This is the exact query from your error
                active_buses = db.session.query(Bus, Schedule, Route, Crew).join(
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

                print(f"   ✅ Complex query successful! Found {len(active_buses)} results")

                if active_buses:
                    bus, schedule, route, crew = active_buses[0]
                    print(f"   📍 Sample result: {bus.registration_number} - {route.route_name} - {crew.name}")

                    # Check if bus has GPS data
                    if hasattr(bus, 'location_lat') and bus.location_lat:
                        print(f"   🗺️  GPS coordinates: ({bus.location_lat}, {bus.location_lng})")
                    else:
                        print("   ❌ Bus missing GPS data")

            except Exception as query_error:
                print(f"   ❌ Query failed: {query_error}")
                print("   🔍 This is likely the source of your error!")
                return False

        print("\n✅ ALL TESTS PASSED!")
        print("🚀 Your Flask app should work perfectly!")
        return True

    except ImportError as import_error:
        print(f"❌ Import error: {import_error}")
        print("🔧 Make sure you're in the correct directory with the Flask app")
        return False

    except Exception as e:
        print(f"❌ Flask app test failed: {e}")
        print("🔍 This is the actual error causing your issue!")
        return False

def check_files_exist():
    """Check if required files exist"""

    required_files = [
        'app/__init__.py',
        'app/models.py',
        'run.py',
        'bus_depot.db'
    ]

    print("📁 Checking required files...")
    missing_files = []

    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path} - MISSING")
            missing_files.append(file_path)

    return len(missing_files) == 0

def main():
    print("=" * 60)
    print("🔍 FLASK APP COMPREHENSIVE TEST")
    print("=" * 60)

    if not check_files_exist():
        print("\n❌ Missing required files! Please make sure you're in the correct directory.")
        return

    print()
    success = test_flask_app()

    print("\n" + "=" * 60)
    if success:
        print("🎉 SUCCESS! Your Flask app is working correctly!")
        print("\n🚀 To start the application:")
        print("   python run.py")
        print("\n🗺️  Then visit the map dashboard:")
        print("   http://localhost:5000/dashboard/map")
    else:
        print("❌ Flask app has issues!")
        print("\n🔧 Check the error message above for the exact problem.")
        print("   This is likely the source of your 'no such column' error.")
    print("=" * 60)

if __name__ == "__main__":
    main()