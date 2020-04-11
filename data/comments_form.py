from flask_wtf import  FlaskForm

from wtforms import TextField, SubmitField
from wtforms.validators import DataRequired

class CommentsForm(FlaskForm):
    comment = TextField('Оставить комментарий', validators=[DataRequired()])
    submit = SubmitField('Отпр.')