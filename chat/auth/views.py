from flask import flash, g, redirect, render_template, request, url_for
from flask_babel import gettext, get_locale
from flask_login import current_user, login_user, logout_user, login_required

from . import auth
from .forms import EmailChangeForm, LoginForm, PasswordChangeForm, RegisterForm, \
    PasswordResetForm, PasswordResetRequestForm
from ..models import db, User
from ..utils import send_mail


@auth.before_app_request
def before_request_handler():
    """Before request handler.
    Envoke before each request to server.
    """
    g.locale = str(get_locale())
    if not current_user.is_anonymous:
        current_user.ping()
        db.session.commit()
    if request.blueprint != "auth":
        if not current_user.is_anonymous and not current_user.confirmed:
            if request.endpoint != "auth.unconfirmed" and request.endpoint != "main.set_language":
                return redirect(url_for("auth.unconfirmed"))       


@auth.route("/login", methods=["GET", "POST"])
def login():
    """Login Page route handler.
    
    :GET - return html page with Login form.
    :POST - verify user credentials and authenticate in case of success.
    """
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data) 
            return redirect(request.args.get("next") or url_for("main.index"))
        flash(gettext("Invalid username or password"), "error")
        return redirect(url_for("auth.login"))
    return render_template("auth/login.html", form=form)


@auth.route("/register", methods=["GET", "POST"])
def register():
    """Register Page route handler.
    
    :GET - return html page with Registration form.
    :POST - validate user data and create account.
    """
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(username=form.username.data,
                    email=form.email.data,
                    password=form.password.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_auth_token()
        send_mail(gettext("Account confirmation"), user.email, "auth/email/account_confirmation", user=user, token=token)
        flash(gettext("Thank you for creating account!"), "success")
        return redirect(url_for("main.index"))
    return render_template("auth/register.html", form=form)


@auth.route("/logout")
@login_required
def logout():
    """Logout Page route handler.
    
    :GET - logout user and redirect to previous page or home page.
    """
    logout_user()
    flash(gettext("You have been logged out."), "success")
    return redirect(request.referrer or url_for('main.index'))


@auth.route("/unconfirmed")
@login_required
def unconfirmed():
    """Unconfirmed account Page route handler.
    
    :GET - if user account is unconfirmed user will be redirected to this page.
    """
    if current_user.confirmed:
        return redirect(url_for("main.index"))
    return render_template("auth/unconfirmed.html")


@auth.route("/confirm/<token>")
@login_required
def confirm(token):
    """Confirm account Page route handler.
    
    :GET - verify confirmation token and confirm account.
    """
    if current_user.verify_auth_token(token):
        db.session.commit()
        flash(gettext("Your account successfully confirmed!"), "success")
    return redirect(url_for("main.index"))


@auth.route("/confirm")
@login_required
def resend_token():
    """Resend confirm token Page route handler.
    
    :GET - resend confirmation token to the user email account.
    """
    if current_user.confirmed:
        return redirect(url_for("main.index"))
    token = current_user.generate_auth_token()
    send_mail(gettext("Account confirmation"), current_user.email, "auth/email/account_confirmation", user=current_user, token=token)
    flash(gettext("An email with confirmation token has been sent to you."), "info")
    return redirect(url_for("auth.unconfirmed"))
    
    
@auth.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():
    """Change password Page route handler.
    
    :GET - return html page with Password change form.
    :POST - validate password and change user credentials.
    """
    form = PasswordChangeForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            db.session.add(current_user)
            db.session.commit()
            flash(gettext("Your password has been changed."), "success")
            return redirect(url_for("main.index"))
        flash(gettext("Invalid old password."), "error")
        return redirect(url_for("auth.change_password"))
    return render_template("auth/change_password.html", form=form)
    
    
@auth.route("/change-email", methods=["GET", "POST"])
@login_required
def change_email():
    """Change email Page route handler.
    
    :GET - return html page with Email change form.
    :POST - generate email change token and send it to new email.
    """
    form = EmailChangeForm()
    if form.validate_on_submit():
        token = current_user.generate_email_token(form.email.data) 
        send_mail(gettext("Change email"), form.email.data, "auth/email/change_email", user=current_user, token=token)
        flash(gettext("Instruction to change email has been sent to you."), "info")
        return redirect(url_for("main.index"))
    return render_template("auth/change_email.html", form=form)


@auth.route("/change-email/<token>")
@login_required
def confirm_change_email(token):
    """Confirm email change token Page route handler.
    
    :GET - confirm email change token and change email address in case of success.
    """
    if current_user.verify_email_token(token):
        db.session.commit()
        flash(gettext("Your email successfully has been changed."), "success")
        return redirect(url_for('main.index'))
    flash(gettext("Invalid email change token."), "error")
    return redirect(url_for('main.index'))


@auth.route("/reset-password", methods=["GET", "POST"])
def request_password_reset():
    """Request reset password Page handler.
    
    :GET - return html page with Request reset password form.
    :POST - send change password token to the user email.
    """
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        token = user.generate_reset_token()
        send_mail(gettext("Reset password"), user.email, "auth/email/request_password_reset", user=user, token=token) 
        flash(gettext("Instruction to reset password has been sent to you."), "info")
        return redirect(url_for("main.index"))
    return render_template("auth/request_password_reset.html", form=form)
  
  
@auth.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    """Reset password Page route handler.
    
    :GET - return html page with Reset password form.
    :POST - verify reset password token and change password in case of success.
    """
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    form = PasswordResetForm()
    if form.validate_on_submit():
        if User.verify_reset_token(token, form.password.data):
            db.session.commit()
            flash(gettext("Your password has been changed."), "success")
            return redirect(url_for("auth.login"))
        flash(gettext("Invalid reset token."), "error")
        return redirect(url_for("main.index"))
    return render_template("auth/reset_password.html", form=form)
    