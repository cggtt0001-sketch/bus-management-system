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

    if not os.path.exists(db_path):
        return

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check if location columns exist in buses table
        cursor.execute("PRAGMA table_info(buses)")
        columns = [row[1] for row in cursor.fetchall()]

        # Add missing columns
        if 'location_lat' not in columns:
            cursor.execute("ALTER TABLE buses ADD COLUMN location_lat REAL")

        if 'location_lng' not in columns:
            cursor.execute("ALTER TABLE buses ADD COLUMN location_lng REAL")

        if 'last_location_update' not in columns:
            cursor.execute("ALTER TABLE buses ADD COLUMN last_location_update DATETIME")

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

        conn.commit()
        conn.close()

    except Exception:
        # Silently handle database errors - let the fix tool handle them
        pass

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
