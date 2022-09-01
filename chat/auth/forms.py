from flask_babel import lazy_gettext as _l
from flask_wtf import FlaskForm, RecaptchaField
from wtforms.fields import EmailField, StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Regexp, ValidationError

from ..models import User


class LoginForm(FlaskForm):
    """Login page form.
    
    :param username: user nickname field.
    :param password: user password field.
    :param remember_me: keep user logged in.
    :param recaptcha: google recaptcha.
    :param submit: subtim button.
    """
    username = StringField(_l("Username"), validators=[DataRequired(), Length(1, 64)])
    password = PasswordField(_l("Password"), validators=[DataRequired()])
    remember_me = BooleanField(_l("Remember me"))
    recaptcha = RecaptchaField()
    submit = SubmitField(_l("Login"))
    
    
class RegisterForm(FlaskForm):
    """Registration page form.
    
    :param username: user nickname field.
    :param email: user email field.
    :param password: user password field.
    :param password2: user repeat password field.
    :param recaptcha: google recaptcha.
    :param submit: subtim button.
    """
    username = StringField(_l("Username"), validators=[DataRequired(), Length(1, 64), 
                                                   Regexp("^[A-Za-z][A-Za-z0-9._]*$", 0, _l("Username should contain"
                                                          "only letters, numbers, dots and underscores."))])
    email = EmailField(_l("Email"), validators=[DataRequired(), Email()])
    password = PasswordField(_l("Password"), validators=[DataRequired(), EqualTo("password2", _l("Passwords must match."))])
    password2 = PasswordField(_l("Repeat password"), validators=[DataRequired()])
    recaptcha = RecaptchaField()
    submit = SubmitField(_l("Sign Up"))


    def validate_username(self, field):
        """Username field validator."""
        if User.query.filter_by(username=field.data).first() is not None:
            raise ValidationError(_l("User with such username already exists."))
        
    def validate_email(self, field):
        """Email field validator."""
        if User.query.filter_by(email=field.data).first() is not None:
            raise ValidationError(_l("Email already in use."))


class PasswordChangeForm(FlaskForm):
    """Password change form.
    
    :param old_password: old user password.
    :param password: new user password.
    :param password2: repeat new user password.
    :param recaptcha: google recaptcha.
    :param submit: subtim button.
    """
    old_password = PasswordField(_l("Old password"), validators=[DataRequired()])
    password = PasswordField(_l("New password"), validators=[DataRequired(), EqualTo("password2", _l("Passwords must match."))])
    password2 = PasswordField(_l("Repeat password"), validators=[DataRequired()])
    recaptcha = RecaptchaField()
    submit = SubmitField(_l("Change password"))


class EmailChangeForm(FlaskForm):
    """Email change form.
    
    :param email: new email.
    :param recaptcha: google recaptcha.
    :param submit: subtim button.
    """
    email = EmailField(_l("New email"), validators=[DataRequired(), Email()])
    recaptcha = RecaptchaField()
    submit = SubmitField(_l("Change email"))
    
    def validate_email(self, field):
        """Email field validator."""
        if User.query.filter_by(email=field.data).first() is not None:
            raise ValidationError(_l("Email already in use."))


class PasswordResetRequestForm(FlaskForm):
    """Password reset request form.
    
    :param email: user email field.
    :param recaptcha: google recaptcha.
    :param submit: subtim button.
    """
    email = EmailField(_l("Email"), validators=[DataRequired(), Email()])
    recaptcha = RecaptchaField()
    submit = SubmitField(_l("Request reset"))
    
    def validate_email(self, field):
        """Email field validator."""
        if User.query.filter_by(email=field.data).first() is None:
            raise ValidationError(_l("Acount with such email not found."))


class PasswordResetForm(FlaskForm):
    """Password reset form.
    
    :param password: new user password.
    :param password2: repeat user password.
    :param recaptcha: google recaptcha.
    :param submit: subtim button.
    """
    password = PasswordField(_l("New password"), validators=[DataRequired(), EqualTo("password2", _l("Passwords must match."))])
    password2 = PasswordField(_l("Repeat password"), validators=[DataRequired()])
    recaptcha = RecaptchaField()
    submit = SubmitField(_l("Reset password"))
