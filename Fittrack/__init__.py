from flask import Flask, redirect, url_for, request
from flask_wtf import CSRFProtect
from .models import db, User
from .config import Config
from flask_login import LoginManager, current_user
from flask_migrate import Migrate
from dotenv import load_dotenv   

load_dotenv()

csrf = CSRFProtect()
login_manager = LoginManager()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    db.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth_bp.signin'
    migrate = Migrate(app, db)

    from .routes import register_blueprints
    register_blueprints(app)   
    if not app.config.get("TESTING", False):
        with app.app_context():
            db.create_all()

    @app.before_request
    def require_profile_completion():
        if current_user.is_authenticated:
            allowed_routes = [
                'auth_bp.logout',
                'profile_bp.basicinfo',
                'static'
            ]
            if not current_user.is_profile_complete:
                if request.endpoint not in allowed_routes and not request.path.startswith("/static"):
                    return redirect(url_for('profile_bp.basicinfo'))

    print("CSRF Protection is enabled:", app.config.get("WTF_CSRF_ENABLED", True))

    return app

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
