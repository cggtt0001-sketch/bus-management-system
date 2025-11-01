import os

class Config:
    """Flask application configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production-bf8a9c4e2d1f'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///bus_system.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
