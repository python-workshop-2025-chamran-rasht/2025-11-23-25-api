from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length


class NewPostForm(FlaskForm):
    content = TextAreaField("Content", validators=[DataRequired(), Length(2, 200)])
    submit = SubmitField("Post")
