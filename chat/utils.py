from threading import Thread

from flask import current_app, render_template
from flask_mail import Message

from .extensions import mail
from .models import db, Category


def async_send_mail(msg, app):
    """Send mail asynchronously.
    
    :param msg: message to send.
    :param app: flask application object.
    """
    with app.app_context():
        mail.send(msg)


def send_mail(subject, to, template_name, **kwargs):
    """Send mail to user.
    
    :param subject: message subject.
    :param to: message recipient.
    :param template_name: name of template to render.
    """
    app = current_app._get_current_object()
    msg = Message(subject) 
    
    msg.sender = app.config["MAIL_USERNAME"]
    msg.recipients = [to]
    msg.body = render_template(template_name + ".txt", **kwargs)
    msg.html = render_template(template_name + ".html", **kwargs)

    thr = Thread(target=async_send_mail, args=[msg, app])
    thr.start()
    return thr


def load_categories(categories=None):
    """Load basic categories to populate database.
    
    :param categories: list of categories to populate db.
    """
    if categories is None:
        categories = ["Python", "Flask", "Django", "JavaScript",
                    "C#", "Java", "C", "C++"]
    for category in categories:
        c = Category(name=category)
        db.session.add(c) 
    db.session.commit() 
    print(f"{len(categories)} categories added successfully.")
