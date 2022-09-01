from flask_babel import lazy_gettext as _l
from flask_wtf import FlaskForm
from wtforms.fields import StringField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length

from ..models import Category


class CreateRoomForm(FlaskForm):
    """Create Room Form.
    
    :param name: room name.
    :param description: room description.
    :param category: room category type.
    :param submit: submit button.
    """
    name = StringField(_l("Room name"), validators=[DataRequired(), Length(1, 128)])
    description = TextAreaField(_l("What is this group about?"))
    category = SelectField(_l("Category"), coerce=int)
    submit = SubmitField(_l("Create room"))
    
    def __init__(self, *args, **kwargs):
        super(CreateRoomForm, self).__init__(*args, **kwargs)
        self.category.choices = [(category.category_id, category.name) for category in Category.query.order_by(Category.name).all()]
    