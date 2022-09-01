from flask import current_app, Blueprint
from flask_sqlalchemy import sqlalchemy as sqla
from ..models import Category, Room

main = Blueprint("main", __name__)

from . import views, errors


@main.app_context_processor 
def context_processor():
    # Display n - 1 categories (1 for All topic).
    limit = current_app.config.get("CATEGORIES_AT_SIDEBAR") - 1
    total_rooms = Room.query.count()
    categories = Category.query.outerjoin(Room).group_by(Category.category_id).order_by(sqla.desc(sqla.func.count(Category.rooms))).limit(limit).all() 
    return {"categories": categories, "total_rooms": total_rooms, "LANGUAGES": current_app.config["LANGUAGES_LIST"]}
