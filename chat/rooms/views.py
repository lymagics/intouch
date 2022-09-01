from flask import current_app, flash, render_template, redirect, request, url_for, session
from flask_babel import gettext
from flask_login import current_user, login_required

from . import rooms
from .forms import CreateRoomForm
from ..models import db, Category, Room


@rooms.route("/rooms/create", methods=["GET", "POST"])
@login_required
def create_room():
    """Create room Page route handler.
    
    :GET - return html page with Create room form.
    :POST - validate form data and create new room in case of success.
    """
    form = CreateRoomForm()
    if form.validate_on_submit():
        category = Category.query.get(form.category.data)
        room = Room(name=form.name.data,
                    description=form.description.data,
                    category=category,
                    creator=current_user) 
        room.users.append(current_user)
        db.session.add(room)
        db.session.commit()
        flash(gettext("Room successfully created."), "success")
        return redirect(url_for("main.index"))
    return render_template("rooms/create_room.html", form=form)


@rooms.route("/rooms/<room_id>")
def room(room_id):
    """Room Page route handler.
    
    :GET - return information about specific room or raise 404 error if room not found.
    """
    room = Room.query.get_or_404(room_id)
    session["room"] = room.room_id
    return render_template("rooms/room.html", room=room)


@rooms.route("/rooms/<room_id>/join")
@login_required
def room_join(room_id):
    """Join room Page route handler.
    
    :GET - add user to the room participants and redirect to room page.
    """
    room = Room.query.get_or_404(room_id)
    if not current_user in room.users:
        room.users.append(current_user)
        db.session.add(room)
        db.session.commit()
        flash(gettext("You have joined %(room)s.", room=room.name), "success") 
    return redirect(url_for("rooms.room", room_id=room_id))


@rooms.route("/category/rooms/<category_id>")
def room_category(category_id):
    """Room category Page route handler.
    
    :GET - return rooms splited by categories.
    """
    category = Category.query.get_or_404(category_id)
    page = request.args.get("page", 1, type=int)
    pagination = Room.query.filter_by(category=category).order_by(Room.created_at.desc()).paginate(
        page=page, per_page=current_app.config["ROOMS_PER_PAGE"]
    )
    rooms = pagination.items
    return render_template("rooms/rooms_by_category.html", rooms=rooms, category=category,
                           pagination=pagination)
