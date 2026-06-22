# app/__init__.py — Flask application factory

from flask import Flask

from app.config import config
from app.extensions import db, socketio, login_manager, migrate



def create_app(config_name='default'):
    """Application factory pattern."""
    app = Flask(
        __name__,
        static_folder="static",
        template_folder="templates"
    )
    app.config.from_object(config[config_name])

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    socketio.init_app(app, async_mode='eventlet')
    login_manager.init_app(app)

    login_manager.login_view = 'auth.login'
    
    # Setup Flask-Login user loader
    from app.models.user import User
    
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))
    
    # Register blueprints
    from app.auth.routes import auth_bp
    from app.api.v1 import api_bp
    from app.views.main import main_bp
    from app.views.fyp import fyp_bp
    from app.views.explore import explore_bp
    from app.views.mutuals import mutuals_bp
    from app.views.messaging import messaging_bp
    from app.views.profile import profile_bp
    from app.views.settings import settings_bp
    from app.views.detail import detail_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(api_bp, url_prefix='/api/v1')
    app.register_blueprint(main_bp)
    app.register_blueprint(fyp_bp, url_prefix='/fyp')
    app.register_blueprint(explore_bp, url_prefix='/explore')
    app.register_blueprint(mutuals_bp, url_prefix='/mutuals')
    app.register_blueprint(messaging_bp, url_prefix='/messaging')
    app.register_blueprint(profile_bp, url_prefix='/profile')
    app.register_blueprint(settings_bp, url_prefix='/settings')
    app.register_blueprint(detail_bp)
    
    # Register SocketIO events
    from app.sockets.events import register_socket_events
    register_socket_events(socketio)
    
    return app
