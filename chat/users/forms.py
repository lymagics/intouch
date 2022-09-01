from flask_babel import lazy_gettext as _l
from flask_wtf import FlaskForm
from wtforms.fields import StringField, TextAreaField, SubmitField


class EditProfileForm(FlaskForm):
    """Edit Profile Form.
    
    :param name: user full name.
    :param about_me: extended user information.
    :param submit: submit button.
    """
    name = StringField(_l("Full Name"))
    about_me = TextAreaField(_l("About Me"))
    submit = SubmitField(_l("Update"))