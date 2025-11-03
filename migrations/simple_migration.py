"""
Simple database migration script to add location fields
"""

import sqlite3
import os

def migrate_database():
    """Add location fields to buses table and create working_hours table"""

    db_path = 'bus_depot.db'

    if not os.path.exists(db_path):
        print("❌ Database file not found. Please run the application first to create the database.")
        return

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Add location columns to buses table
        print("Adding location fields to buses table...")
        cursor.execute("ALTER TABLE buses ADD COLUMN location_lat REAL")
        print("✅ Added location_lat column")

        cursor.execute("ALTER TABLE buses ADD COLUMN location_lng REAL")
        print("✅ Added location_lng column")

        cursor.execute("ALTER TABLE buses ADD COLUMN last_location_update DATETIME")
        print("✅ Added last_location_update column")

        # Create working_hours table
        print("Creating working_hours table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS working_hours (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                crew_id INTEGER NOT NULL,
                date DATE NOT NULL,
                hours_worked REAL NOT NULL,
                schedule_id INTEGER,
                FOREIGN KEY (crew_id) REFERENCES crew (id),
                FOREIGN KEY (schedule_id) REFERENCES schedules (id)
            )
        """)
        print("✅ Created working_hours table")

        # Update existing active buses with mock coordinates
        print("Updating active buses with mock coordinates...")
        cursor.execute("""
            UPDATE buses
            SET location_lat = 40.7128 + (RANDOM() % 1000 - 500) * 0.0001,
                location_lng = -74.0060 + (RANDOM() % 1000 - 500) * 0.0001,
                last_location_update = datetime('now')
            WHERE status = 'active'
        """)

        updated_rows = cursor.rowcount
        print(f"✅ Updated {updated_rows} active buses with mock coordinates")

        conn.commit()
        conn.close()

        print("\n🎉 Migration completed successfully!")

    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        if conn:
            conn.rollback()
            conn.close()
    except Exception as e:
        print(f"❌ Migration error: {e}")
        if conn:
            conn.close()

if __name__ == "__main__":
    migrate_database()