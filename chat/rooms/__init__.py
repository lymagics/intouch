from flask import Blueprint

rooms = Blueprint("rooms", __name__)

from . import views, events
