"""
Setup script to create database and run migrations
"""

import sqlite3
import os
from datetime import datetime

def create_database():
    """Create the database with basic tables"""

    db_path = 'bus_depot.db'

    if os.path.exists(db_path):
        os.remove(db_path)
        print("Removed existing database")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create buses table
    cursor.execute("""
        CREATE TABLE buses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            registration_number VARCHAR(50) UNIQUE NOT NULL,
            capacity INTEGER NOT NULL,
            model VARCHAR(100),
            status VARCHAR(20) DEFAULT 'active',
            purchase_date DATE,
            location_lat REAL,
            location_lng REAL,
            last_location_update DATETIME
        )
    """)

    # Create routes table
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

    # Create schedules table
    cursor.execute("""
        CREATE TABLE schedules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
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

    # Create crew table
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

    # Create crew_assignments table
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

    # Create working_hours table
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

    # Insert sample data
    print("Inserting sample data...")

    # Sample routes
    routes_data = [
        ('Downtown Express', 'Central Station', 'Airport', 25.5, 'Main St, 5th Ave, Airport Rd'),
        ('City Circular', 'Bus Terminal', 'Bus Terminal', 15.0, 'All major city stops'),
        ('University Route', 'Campus North', 'Downtown', 8.2, 'Campus areas, shopping district'),
        ('Suburban Connector', 'Suburb Mall', 'City Center', 12.8, 'Residential areas, office park')
    ]

    cursor.executemany("INSERT INTO routes (route_name, start_point, end_point, distance, stops) VALUES (?, ?, ?, ?, ?)", routes_data)

    # Sample crew
    crew_data = [
        ('DRV001', 'John Smith', 'Driver', '555-0101', '2023-01-15'),
        ('DRV002', 'Sarah Johnson', 'Driver', '555-0102', '2023-02-20'),
        ('COND001', 'Mike Wilson', 'Conductor', '555-0103', '2023-03-10'),
        ('COND002', 'Emily Davis', 'Conductor', '555-0104', '2023-04-05'),
        ('MAINT001', 'Robert Brown', 'Maintenance Staff', '555-0105', '2023-01-20')
    ]

    cursor.executemany("INSERT INTO crew (crew_id, name, role, contact_info, hire_date) VALUES (?, ?, ?, ?, ?)", crew_data)

    # Sample buses
    buses_data = [
        ('BUS001', 45, 'Mercedes Citaro', 'active', '2023-01-01', 40.7128, -74.0060, datetime.now()),
        ('BUS002', 50, 'Volvo 7900', 'active', '2023-02-15', 40.7589, -73.9851, datetime.now()),
        ('BUS003', 40, 'MAN Lion\'s City', 'active', '2023-03-20', 40.7282, -73.9942, datetime.now()),
        ('BUS004', 55, 'Alexander Dennis', 'maintenance', '2022-12-01', None, None, None),
        ('BUS005', 35, 'Irisbus Crossway', 'inactive', '2022-10-15', None, None, None)
    ]

    cursor.executemany("INSERT INTO buses (registration_number, capacity, model, status, purchase_date, location_lat, location_lng, last_location_update) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", buses_data)

    # Sample schedules
    schedules_data = [
        (1, 1, '08:00:00', '17:00:00', 'daily', 1),
        (2, 2, '09:00:00', '18:00:00', 'daily', 1),
        (3, 3, '07:30:00', '16:30:00', 'daily', 1),
        (1, 1, '18:30:00', '23:00:00', 'daily', 1)
    ]

    cursor.executemany("INSERT INTO schedules (route_id, bus_id, departure_time, arrival_time, frequency, active) VALUES (?, ?, ?, ?, ?, ?)", schedules_data)

    # Sample crew assignments
    assignments_data = [
        (1, 1, '2025-01-01', 'Morning shift'),
        (1, 3, '2025-01-01', 'Morning shift'),
        (2, 2, '2025-01-01', 'Morning shift'),
        (2, 4, '2025-01-01', 'Morning shift'),
        (3, 1, '2025-01-01', 'Afternoon shift'),
        (3, 3, '2025-01-01', 'Afternoon shift'),
        (4, 2, '2025-01-01', 'Evening shift'),
        (4, 4, '2025-01-01', 'Evening shift')
    ]

    cursor.executemany("INSERT INTO crew_assignments (schedule_id, crew_id, assignment_date, notes) VALUES (?, ?, ?, ?)", assignments_data)

    # Sample working hours
    import random
    working_hours_data = []
    for crew_id in range(1, 6):  # 5 crew members
        for day in range(1, 31):  # 30 days of data
            hours = round(random.uniform(6, 10), 1)  # 6-10 hours per day
            working_hours_data.append((crew_id, f'2025-01-{day:02d}', hours, None))

    cursor.executemany("INSERT INTO working_hours (crew_id, date, hours_worked, schedule_id) VALUES (?, ?, ?, ?)", working_hours_data)

    conn.commit()
    conn.close()

    print("✅ Database created successfully with sample data!")
    print(f"📍 Database location: {os.path.abspath(db_path)}")
    print("🚌 Sample buses: 5")
    print("🛣️ Sample routes: 4")
    print("👥 Sample crew: 5")
    print("📅 Sample schedules: 4")
    print("⏰ Sample working hours: 150")

if __name__ == "__main__":
    create_database()