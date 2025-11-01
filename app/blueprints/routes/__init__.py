from flask import Blueprint

routes_bp = Blueprint('routes', __name__)

from app.blueprints.routes import routes as route_handlers
