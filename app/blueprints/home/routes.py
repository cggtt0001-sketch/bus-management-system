from flask import render_template
from app.blueprints.home import home_bp

@home_bp.route('/')
def index():
    """Homepage with navigation cards to all modules"""
    return render_template('home/index.html')
