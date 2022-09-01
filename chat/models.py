import hashlib
from datetime import datetime, timedelta, timezone

import jwt
from flask import current_app
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from .extensions import db, login_manager


# SQLAlchemy table to represent many-to-many relationship between "rooms" and "users" tables.
participants = db.Table("participants",
    db.Column("room_id", db.Integer, db.ForeignKey("rooms.room_id"), primary_key=True),
    db.Column("user_id", db.Integer, db.ForeignKey("users.user_id"), primary_key=True)
)


class Searchable:
    """Class to extend sqlalchemy models with search."""
    @classmethod
    def search(cls, query):
        """Search method.
        
        :param query: query string to search.
        """
        likes = []
        for field in cls.__searchable__:
            if hasattr(cls, field):
                attr = getattr(cls, field)
                likes.append(attr.like(f"%{query}%"))
        return cls.query.filter(db.or_(*likes))
    
    
class Category(db.Model):
    """SQLAlchemy model to represent "categories" table.
    
    :param category_id: unique primary key.
    :param name: category name.
    :param rooms: sqlalchemy orm relationship with "rooms" table.
    """
    __tablename__ = "categories"
    
    category_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    
    rooms = db.relationship("Room", backref="category", cascade="all,delete", lazy="dynamic")
    
    def __repr__(self):
        return f"<Category {self.name}>"
    

class Room(Searchable, db.Model):
    """SQLAlchemy model to represent "rooms" table.
    
    :param room_id: unique primary key.
    :param name: rooms name.
    :param description: room description.
    :param created_at: date and time when room was created.
    :param creator_id: [foreign key] room creator identifier.
    :param category_id: [foreign key] category identifier.
    :param messages: sqlalchemy orm relationship with "messages" table.
    :param messages: sqlalchemy orm relationship with "users" table.
    """
    __tablename__ = "rooms"
    __searchable__ = ["name", "description"]
    
    room_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), index=True)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    creator_id = db.Column(db.Integer, db.ForeignKey("users.user_id"))
    category_id = db.Column(db.Integer, db.ForeignKey("categories.category_id"))
    
    messages = db.relationship("Message", backref="room", cascade="all,delete", lazy="dynamic")
    users = db.relationship("User", secondary=participants, lazy="dynamic", backref=db.backref("rooms", lazy="dynamic"))
    
    def clean(self):
        """Delete messages if there are more than available."""
        messages_count = self.messages.count()
        if messages_count > current_app.config["MAX_MESSAGES_AVAILABLE"]:
            distance = messages_count - current_app.config["MAX_MESSAGES_AVAILABLE"]
            messages = self.messages.order_by(Message.sent_at).limit(distance).all()
            for message in messages:
                db.session.delete(message)

    def __repr__(self):
        return f"<Room {self.name}>"
    
    
class Message(db.Model):
    """SQLAlchemy model to represent "messages" table.
    
    :param message_id: unique primary key.
    :param text: message body.
    :param sent_at: date and time message was send.
    :param sender_id: [foreign key] message sender identifier.
    :param room_id: [foreign key] room message was send identifier.
    """
    __tablename__ = "messages"
    
    message_id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(200))
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)
    sender_id = db.Column(db.Integer, db.ForeignKey("users.user_id"))
    room_id = db.Column(db.Integer, db.ForeignKey("rooms.room_id"))
    
    
class User(UserMixin, db.Model):
    """SQLAlchemy model to represent "users" table.
    
    :param users_id: unique primary key.
    :param username: unique user nickname.
    :param about_me: extended information about user.
    :param confirmed: is user email confirmed.
    :param email: unique user email address.
    :param gravatar_hash: user email hash for gravatar service.
    :param last_seen: date and time user was last seen.
    :param member_since: date and time user joined service.
    :param name: full user name.
    :param password: user password.
    :param password_hash: hash value of user password.
    :param rooms_owned: sqlalchemy orm relationship with "rooms" table.
    :param messages: sqlalchemy orm relationship with "messages" table.
    """
    __tablename__ = "users"
    
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    about_me = db.Column(db.Text)
    confirmed = db.Column(db.Boolean, default=False)
    email = db.Column(db.String(64), unique=True, index=True)
    gravatar_hash = db.Column(db.String(32))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    member_since = db.Column(db.DateTime, default=datetime.utcnow)
    name = db.Column(db.String(64))
    password = db.Column(db.String(64))
    password_hash = db.Column(db.String(128))
    
    rooms_owned = db.relationship("Room", backref="creator", cascade="all,delete", lazy="dynamic")
    messages = db.relationship("Message", backref="sender", cascade="all,delete", lazy="dynamic")
    
    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        self.gravatar_hash = hashlib.md5(self.email.encode("utf-8")).hexdigest()
    
    def generate_auth_token(self, expiration=3600):
        """Generate account confirmation token.
        
        :param expiration: time in seconds when token is valid.
        """
        return jwt.encode(
            {
                "user_id": self.user_id,
                "exp": datetime.now(timezone.utc) + timedelta(seconds=expiration),
            }, 
            current_app.config["SECRET_KEY"],
            algorithm="HS256"
        )
        
    def verify_auth_token(self, token):
        """Verify account confirmation token.
        
        :param token: account confirmation token.
        """
        try:
            data = jwt.decode(
                token,
                current_app.config["SECRET_KEY"],
                algorithms=["HS256"]
            )
        except:
            return False 
        if data.get("user_id") != self.user_id:
            return False 
        self.confirmed = True 
        db.session.add(self)
        return True
    
    def generate_email_token(self, new_email, expiration=3600):
        """Generate email change token.
        
        :param new_email: new email address.
        :param expiration: time in seconds when token is valid.
        """
        return jwt.encode(
            {
                "user_id": self.user_id,
                "email": new_email,
                "exp": datetime.now(timezone.utc) + \
                    timedelta(seconds=expiration)
            },
            current_app.config["SECRET_KEY"],
            algorithm="HS256"
        )
        
    def verify_email_token(self, token):
        """Verify email change token.
        
        :param token: email change token.
        """
        try:
            data = jwt.decode(
                token,
                current_app.config["SECRET_KEY"],
                algorithms=["HS256"]
            )
        except:
            return False 
        if not data.get("user_id") or not data.get("email"):
            return False 
        if self.user_id != data["user_id"]:
            return False 
        self.email = data["email"]
        db.session.add(self)
        return True
    
    def generate_reset_token(self, expiration=3600):
        """Generate password reset token.
        
        :param expiration: time in seconds when token is valid.
        """
        return jwt.encode(
            {
                "user_id": self.user_id,
                "exp": datetime.now(timezone.utc) + \
                    timedelta(seconds=expiration)
            },
            current_app.config["SECRET_KEY"],
            algorithm="HS256"
        )
        
    @staticmethod
    def verify_reset_token(token, new_password):
        """Verify password reset token.
        
        :param token: password reset token.
        :param new_password: new user password.
        """
        try:
            data = jwt.decode(
                token,
                current_app.config["SECRET_KEY"],
                algorithms=["HS256"]
            )
        except:
            return False 
        if not data.get("user_id"):
            return False 
        user = User.query.get(data["user_id"])
        if user is None:
            return False 
        user.password = new_password
        db.session.add(user)
        return True
    
    def gravatar_url(self, size=16, default="mp", rating="g"):
        """Generate url for gravatar service.
        
        :param size: image size in pixels.
        :param default: default image if user doesn't have account on gravatar.
        :param rating: user image rating.
        """
        url = self.gravatar_hash or hashlib.md5(self.email.encode("utf-8")).hexdigest()
        return f"https://www.gravatar.com/avatar/{url}?s={size}&d={default}&r={rating}"
    
    @property
    def password(self):
        """Password getter. Raise [AttributeError] in case some try to access it."""
        raise AttributeError("Password filed can't be accessed!")
    
    @password.setter
    def password(self, password):
        """Password setter. Make hash from raw password.
        
        :param password: user password.
        """
        self.password_hash = generate_password_hash(password)
    
    def ping(self):
        """User last seen tracker."""
        self.last_seen = datetime.utcnow()
        db.session.add(self)
    
    def verify_password(self, password):
        """Check if user enter right password."""
        return check_password_hash(self.password_hash, password)
    
    def __getattr__(self, attr):
        if attr == "id":
            return self.user_id
        raise AttributeError(f"User model doesn't have attribute {attr}.")
    
    def __repr__(self):
        return f"<User {self.username}>"
  
  
@login_manager.user_loader
def load_user(user_id):
    """Reload the user object from the user ID stored in the session.
    
    :param user_id: unique user identifier.
    """
    return User.query.get(user_id)
    