from flask import Blueprint

buses_bp = Blueprint('buses', __name__)

from app.blueprints.buses import routes
