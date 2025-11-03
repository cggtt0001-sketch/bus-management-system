from flask import Flask, render_template
from flask_wtf.csrf import CSRFProtect
from config import Config
from app.models import db
import sqlite3
import os

csrf = CSRFProtect()

def ensure_database_schema():
    """Ensure database has required columns and tables"""
    db_path = 'bus_depot.db'

    # Create database if it doesn't exist
    if not os.path.exists(db_path):
        print("📋 Database not found. Running migration...")
        try:
            import subprocess
            import sys
            result = subprocess.run([sys.executable, 'migrate_database.py'],
                                  capture_output=True, text=True, cwd=os.path.dirname(__file__) + '/..')
            if result.returncode == 0:
                print("✅ Database created and migrated successfully")
            else:
                print(f"❌ Migration failed: {result.stderr}")
        except Exception as e:
            print(f"❌ Error running migration: {e}")
        return

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check if location columns exist in buses table
        cursor.execute("PRAGMA table_info(buses)")
        columns = [row[1] for row in cursor.fetchall()]
        required_columns = ['location_lat', 'location_lng', 'last_location_update']

        missing_columns = [col for col in required_columns if col not in columns]

        if missing_columns:
            print(f"🔧 Database missing columns: {', '.join(missing_columns)}")
            print("🔧 Running automatic migration...")

            # Add missing columns
            for col in missing_columns:
                if col == 'location_lat':
                    cursor.execute("ALTER TABLE buses ADD COLUMN location_lat REAL")
                elif col == 'location_lng':
                    cursor.execute("ALTER TABLE buses ADD COLUMN location_lng REAL")
                elif col == 'last_location_update':
                    cursor.execute("ALTER TABLE buses ADD COLUMN last_location_update DATETIME")
                print(f"✅ Added column: {col}")

            # Check if working_hours table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='working_hours'")
            if not cursor.fetchone():
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
                print("✅ Created working_hours table")

            conn.commit()
            print("✅ Database schema updated successfully")
        else:
            print("✅ Database schema is up to date")

        conn.close()

    except Exception as e:
        print(f"❌ Error updating database schema: {e}")
        # Try to run the migration script as fallback
        try:
            import subprocess
            import sys
            result = subprocess.run([sys.executable, 'migrate_database.py'],
                                  capture_output=True, text=True, cwd=os.path.dirname(__file__) + '/..')
            if result.returncode == 0:
                print("✅ Migration script completed successfully")
            else:
                print(f"❌ Migration script failed: {result.stderr}")
        except Exception as migration_error:
            print(f"❌ Migration script error: {migration_error}")

def create_app(config_class=Config):
    """Flask application factory"""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    csrf.init_app(app)

    # Ensure database schema is up to date
    ensure_database_schema()

    # Register blueprints
    from app.blueprints.home import home_bp
    from app.blueprints.buses import buses_bp
    from app.blueprints.routes import routes_bp
    from app.blueprints.schedules import schedules_bp
    from app.blueprints.crew import crew_bp
    from app.blueprints.dashboard import dashboard_bp
    from app.blueprints.reports import reports_bp

    app.register_blueprint(home_bp)
    app.register_blueprint(buses_bp, url_prefix='/buses')
    app.register_blueprint(routes_bp, url_prefix='/routes')
    app.register_blueprint(schedules_bp, url_prefix='/schedules')
    app.register_blueprint(crew_bp, url_prefix='/crew')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(reports_bp, url_prefix='/reports')

    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500

    return app
