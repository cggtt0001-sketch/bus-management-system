from flask import Flask, render_template
from flask_wtf.csrf import CSRFProtect
from config import Config
from app.models import db
import sqlite3
import os

csrf = CSRFProtect()

def create_app(config_class=Config):
    """Flask application factory"""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    csrf.init_app(app)

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
