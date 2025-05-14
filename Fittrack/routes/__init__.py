def register_blueprints(app):
    from .main_routes import main_bp
    from .auth_routes import auth_bp
    from .profile_routes import profile_bp
    from .upload_routes import upload_bp
    from .visualise_routes import visualise_bp
    from .friends_routes import friends_bp  
    from .share_routes import share_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(upload_bp)
    app.register_blueprint(visualise_bp)
    app.register_blueprint(friends_bp)
    app.register_blueprint(share_bp)
