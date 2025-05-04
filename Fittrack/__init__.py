from flask import Flask
from .models import db
from .routes import register_routes

def create_app():
    app = Flask(__name__)
    app.secret_key = 'group10'

    # Cookie/session configuration for dev environment
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['SESSION_COOKIE_SECURE'] = False
    # Set up the database URI
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize SQLAlchemy
    db.init_app(app)

    # Create a table in the application context
    with app.app_context():
        db.create_all()

    # routes
    register_routes(app)

    return app
