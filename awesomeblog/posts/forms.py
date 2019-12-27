from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length


class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=1, max=164)])
    body = TextAreaField('Body', validators=[DataRequired()])
    submit = SubmitField('Submit')
