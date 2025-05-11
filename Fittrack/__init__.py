from flask import Flask
from flask_wtf import CSRFProtect
from .models import db

csrf = CSRFProtect()

def create_app():
    app = Flask(__name__)
    app.secret_key = 'group10'

    # Session & CSRF config
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['SESSION_COOKIE_SECURE'] = False
    app.config['WTF_CSRF_SECRET_KEY'] = 'another-strong-secret'

    # Database config
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Init extensions
    db.init_app(app)
    csrf.init_app(app)

    # Register all route blueprints
    from .routes import register_blueprints
    register_blueprints(app)

    with app.app_context():
        db.create_all()

    return app

