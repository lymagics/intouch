from flask import render_template
from . import main


@main.app_errorhandler(400)
def bad_request(e):
    """HTTP 400 error handler."""
    return render_template("errors/400.html")


@main.app_errorhandler(403)
def forbidden(e):
    """HTTP 403 error handler."""
    return render_template("errors/403.html")


@main.app_errorhandler(404)
def page_not_found(e):
    """HTTP 404 error handler."""
    return render_template("errors/404.html")


@main.app_errorhandler(500)
def internal_server_error(e):
    """HTTP 500 error handler."""
    return render_template("errors/500.html")
