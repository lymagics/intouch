import sqlalchemy as sqla
from flask import flash, redirect, render_template, url_for
from flask_babel import gettext
from flask_login import current_user, login_required

from . import users
from .forms import EditProfileForm
from ..models import db, User, Room, Message


@users.route("/users/<username>")
def user_page(username):
    """User Page route handler.
    
    :GET - return html page with specific user information.
    """
    user = User.query.filter_by(username=username).first_or_404()
    rooms = user.rooms.order_by(Room.created_at.desc()).limit(5).all()
    return render_template("users/user_page.html", user=user, rooms=rooms)


@users.route("/users/edit", methods=["GET", "POST"])
@login_required
def edit_user():
    """Edit user Page route handler.
    
    :GET - return html page with Edit user form.
    :POST - validate data and change user information in case of success.
    """
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data 
        current_user.about_me = form.about_me.data 
        db.session.add(current_user)
        db.session.commit()
        flash(gettext("Profile info successfully updated."), "success")
        return redirect(url_for("users.user_page", username=current_user.username))
    form.name.data = current_user.name 
    form.about_me.data = current_user.about_me
    return render_template("users/edit_profile.html", form=form)
