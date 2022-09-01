import os
from dotenv import load_dotenv 

load_dotenv()
# Base directory for local database.
base_dir = os.path.abspath(os.path.dirname(__file__))


def as_bool(val):
    """Config boolean value loader."""
    if val.lower() in ["yes", "true", "1"]:
        return True 
    return False


class Config:
    """Application config class. Can be used in app.from_object method."""
    # Secret key for data encryption.
    SECRET_KEY = os.environ.get("SECRET_KEY", "!h2n3a8cp")
    
    # URL to database.
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "").replace('postgres://', 'postgresql://') or \
        "sqlite:///" + os.path.join(base_dir, "database.sqlite")
        
    # Mail system settings.
    MAIL_SERVER = os.environ.get("MAIL_SERVER")
    MAIL_PORT = os.environ.get("MAIL_PORT")
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    MAIL_USE_TLS = as_bool(os.environ.get("MAIL_USE_TLS", ""))

    # Google recaptcha settings.
    RECAPTCHA_PUBLIC_KEY = os.environ.get("RECAPTCHA_PUBLIC_KEY")
    RECAPTCHA_PRIVATE_KEY = os.environ.get("RECAPTCHA_PRIVATE_KEY")
    RECAPTCHA_DATA_ATTRS = {'theme': 'dark'}
    
    # Pagination setting.
    CATEGORIES_AT_SIDEBAR = os.environ.get("CATEGORIES_AT_SIDEBAR", 5)
    ROOMS_PER_PAGE = os.environ.get("ROOMS_PER_PAGE", 5)
    
    # Maximum messages per chat.
    MAX_MESSAGES_AVAILABLE = os.environ.get("MAX_MESSAGES_AVAILABLE", 20)
    
    # Application languages available
    LANGUAGES_LIST = {
        "en": "ENG",
        "ru": "РУС",
        "uk": "УКР"
    }
    
    
class TestConfig:
    """Application test config class."""
    # Enable testing mode.
    TESTING = True
    
    # Secret key for data encryption.
    SECRET_KEY = os.environ.get("TEST_SECRET_KEY", "test key!")
    
    # URL to test database.
    SQLACHEMY_DATABASE_URI = os.environ.get("TEST_DATABASE_URL") or \
        "sqlite:///" + os.path.join(base_dir, "testdb.sqlite") 
    
    # Pagination setting. 
    ROOMS_PER_PAGE = os.environ.get("ROOMS_PER_PAGE", 5)
    
    # Maximum messages per chat.
    MAX_MESSAGES_AVAILABLE = os.environ.get("MAX_MESSAGES_AVAILABLE", 20)
