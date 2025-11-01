from flask import Blueprint

crew_bp = Blueprint('crew', __name__)

from app.blueprints.crew import routes
