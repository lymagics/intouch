from flask import current_app, request
from flask_sqlalchemy import SQLAlchemy
from flask_babel import Babel, lazy_gettext as _l
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_moment import Moment
from flask_socketio import SocketIO

babel = Babel()
db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()
migrate = Migrate(compare_type=True)
moment = Moment()
sio = SocketIO()

# Flask-login settings
login_manager.login_view = "auth.login"
login_manager.login_message = _l("Please log in to access this page.")
login_manager.login_message_category = "info"
login_manager.session_protection = "strong"


@babel.localeselector
def get_locale():
    lang = request.cookies.get("lang")
    return lang or request.accept_languages.best_match(current_app.config["LANGUAGES_LIST"].keys())
