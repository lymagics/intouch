from flask import session
from flask_login import current_user
from flask_socketio import join_room, leave_room

from ..extensions import sio 
from ..models import db, Room, Message


@sio.on("connect", namespace="/room")
def on_connect():
    """SocketIO on connect event. Envoke when user connect to the page."""
    room = session.get("room")
    join_room(room)
   
   
@sio.on("new-message", namespace="/room")
def on_new_message(data):
    """SocketIO on new message event. Envoke when user send new message to the room."""
    room = Room.query.get_or_404(session.get("room"))
    message = Message(text=data.get("msg"), sender=current_user, room=room)
    db.session.add(message)
    room.clean()
    db.session.commit()
    ctx = {
        "msg": message.text,
        "username": current_user.username,
        "sent_at": str(message.sent_at),
        "avatar": current_user.gravatar_url(25)
    }
    sio.emit("new_message", ctx, namespace="/room", to=room.room_id)
        
        
@sio.on("disconnect", namespace="/room")
def on_disconnect():
    """SocketIO on disconnect event. Envoke when user disconnect from the page."""
    room = session.get("room")
    leave_room(room)
    