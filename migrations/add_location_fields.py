"""
Database migration script to add location fields to Bus model
Run this script to update the database schema
"""

from app import create_app, db
from app.models import Bus
from sqlalchemy import text
import random
from datetime import datetime

def migrate_location_fields():
    """Add location fields to buses table"""

    app = create_app()

    with app.app_context():
        try:
            # Add location_lat column
            db.session.execute(text("""
                ALTER TABLE buses ADD COLUMN location_lat FLOAT
            """))

            # Add location_lng column
            db.session.execute(text("""
                ALTER TABLE buses ADD COLUMN location_lng FLOAT
            """))

            # Add last_location_update column
            db.session.execute(text("""
                ALTER TABLE buses ADD COLUMN last_location_update DATETIME
            """))

            # Create working_hours table
            db.session.execute(text("""
                CREATE TABLE IF NOT EXISTS working_hours (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    crew_id INTEGER NOT NULL,
                    date DATE NOT NULL,
                    hours_worked FLOAT NOT NULL,
                    schedule_id INTEGER,
                    FOREIGN KEY (crew_id) REFERENCES crew (id),
                    FOREIGN KEY (schedule_id) REFERENCES schedules (id)
                )
            """))

            db.session.commit()
            print("✅ Location fields added successfully!")

            # Update existing buses with mock coordinates
            buses = Bus.query.filter_by(status='active').all()
            for bus in buses:
                bus.location_lat = 40.7128 + (random.random() - 0.5) * 0.1
                bus.location_lng = -74.0060 + (random.random() - 0.5) * 0.1
                bus.last_location_update = datetime.utcnow()

            db.session.commit()
            print(f"✅ {len(buses)} active buses updated with mock coordinates!")

        except Exception as e:
            db.session.rollback()
            print(f"❌ Migration failed: {e}")

if __name__ == "__main__":
    migrate_location_fields()