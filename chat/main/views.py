from flask import current_app, redirect, request, render_template, url_for, make_response

from . import main
from ..models import Room


@main.route("/")
def index():
    """Home Page route handler.
    
    :GET - return html page with recently created rooms.
    """
    page = request.args.get("page", 1, type=int)
    pagination = Room.query.order_by(Room.created_at.desc()).paginate(
        page=page, per_page=current_app.config["ROOMS_PER_PAGE"]
    )
    rooms = pagination.items
    return render_template("index.html", rooms=rooms, pagination=pagination)


@main.route("/search")
def search():
    """Search Page route handler.
    
    :GET - search for rooms in database and return result.
    """
    q = request.args.get("q")
    if q is None:
        return redirect(url_for("main.index"))
    
    page = request.args.get("page", 1, type=int)
    query = Room.search(q)
    
    pagination = query.paginate(
        page=page, per_page=current_app.config["ROOMS_PER_PAGE"]
    )
    rooms = pagination.items
    return render_template("rooms/search.html", pagination=pagination, rooms=rooms, q=q)


@main.route("/language")
def set_language():
    """Set language Page route handler.
    
    :GET - set site language in cookies and redirect to referrer or home page.
    """
    code = request.args.get("lang", "en")
    lang = code if code in current_app.config["LANGUAGES_LIST"] else "en"
    response = make_response(redirect(request.referrer or url_for("main.index")))
    response.set_cookie("lang", lang, max_age=60*60*24*90)
    return response
