#!/usr/bin/env python3
"""
Bus Depot Management System - Startup Script
Automatically checks and fixes database issues before starting the application
"""

import os
import sys
import sqlite3
import subprocess

def check_database_health():
    """Check if the database is healthy and has all required features"""
    db_path = 'bus_depot.db'

    # If database doesn't exist, create it
    if not os.path.exists(db_path):
        print("📋 Database not found. Creating new database...")
        try:
            result = subprocess.run([sys.executable, 'setup_database.py'],
                                  capture_output=True, text=True, check=True)
            print("✅ Database created successfully!")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to create database: {e}")
            print("Please run 'python fix_database.py' manually")
            return False

    # Check database structure
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check if buses table has required columns
        cursor.execute("PRAGMA table_info(buses)")
        columns = [row[1] for row in cursor.fetchall()]
        required_columns = ['location_lat', 'location_lng', 'last_location_update']

        missing_columns = [col for col in required_columns if col not in columns]

        # Check if working_hours table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='working_hours'")
        working_hours_exists = cursor.fetchone() is not None

        conn.close()

        if missing_columns or not working_hours_exists:
            print("⚠️  Database needs updates...")
            print("🔧 Running automatic database fix...")
            try:
                result = subprocess.run([sys.executable, 'fix_database.py'],
                                      capture_output=True, text=True, check=True)
                print("✅ Database fixed successfully!")
                return True
            except subprocess.CalledProcessError as e:
                print(f"❌ Automatic fix failed: {e}")
                print("Please run 'python fix_database.py' manually")
                return False
        else:
            print("✅ Database is healthy!")
            return True

    except Exception as e:
        print(f"❌ Database health check failed: {e}")
        print("Please run 'python fix_database.py' manually")
        return False

def start_application():
    """Start the Flask application"""
    print("\n🚀 Starting Bus Depot Management System...")
    print("=" * 60)

    try:
        # Import and run the Flask app
        from run import app
        print("🌐 Starting web server...")
        print("📍 Application will be available at: http://localhost:5000")
        print("🗺️  Live Map: http://localhost:5000/dashboard/map")
        print("=" * 60)
        app.run(debug=True, host='0.0.0.0', port=5000)

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please make sure you have all dependencies installed:")
        print("pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"❌ Failed to start application: {e}")
        return False

def main():
    """Main startup function"""
    print("=" * 60)
    print("🚌 Bus Depot Management System - Startup")
    print("=" * 60)

    # Check if we're in the right directory
    if not os.path.exists('run.py'):
        print("❌ Please run this script from the project root directory")
        print("   (where run.py is located)")
        sys.exit(1)

    # Check and fix database
    if not check_database_health():
        print("\n❌ Database setup failed. Cannot start application.")
        print("Please run 'python fix_database.py' to resolve database issues.")
        sys.exit(1)

    # Start the application
    start_application()

if __name__ == "__main__":
    main()