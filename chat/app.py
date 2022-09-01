from flask import Flask
from config import Config
from .models import db, participants, Category, Message, Room, User


def create_app(config=Config):
    """Flask application factory.
    
    :param config: application config.
    """
    app = Flask(__name__)
    app.config.from_object(config)
    
    register_blueprints(app)
    register_extensions(app)
    
    @app.shell_context_processor
    def shell_context():
        """Register shell context."""
        return {"db": db, "participants": participants, "Category": Category, 
                "Message": Message, "Room": Room, "User": User}
    
    return app 


def register_blueprints(app):
    """Register application blueprints."""
    from .main import main
    app.register_blueprint(main)
    
    from .auth import auth
    app.register_blueprint(auth, url_prefix="/auth")
    
    from .rooms import rooms
    app.register_blueprint(rooms)
    
    from .users import users 
    app.register_blueprint(users)
    
    
def register_extensions(app):
    """Register application extensions."""
    from .extensions import babel 
    babel.init_app(app)
    
    from .extensions import db 
    db.init_app(app)
    
    from .extensions import login_manager
    login_manager.init_app(app)

    from .extensions import migrate
    migrate.init_app(app, db)
    
    from .extensions import mail
    mail.init_app(app)
    
    from .extensions import moment
    moment.init_app(app)
    
    from .extensions import sio 
    sio.init_app(app)
    