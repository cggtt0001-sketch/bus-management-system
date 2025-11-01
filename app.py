from flask import Flask
from models import db
from blueprints.main import main_bp
from blueprints.schedule import schedule_bp
from blueprints.bus import bus_bp
from blueprints.route import route_bp

def create_app():
    """Application factory for creating Flask app instance"""
    app = Flask(__name__)

    # Load configuration
    app.config.from_object('config.Config')

    # Initialize database
    db.init_app(app)

    # Register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(schedule_bp)
    app.register_blueprint(bus_bp)
    app.register_blueprint(route_bp)

    # Create database tables if they don't exist
    with app.app_context():
        db.create_all()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
