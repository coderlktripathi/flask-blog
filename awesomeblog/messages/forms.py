from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length


class MessageForm(FlaskForm):
    message = TextAreaField(
        'Message', validators=[DataRequired(), Length(min=0, max=140)]
    )
    submit = SubmitField('Submit')
