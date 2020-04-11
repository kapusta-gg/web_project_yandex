from flask_wtf import  FlaskForm

from wtforms import TextField, SubmitField
from wtforms.validators import InputRequired

class CommentsForm(FlaskForm):
    comment = TextField('Оставить комментарий', validators=[InputRequired()])
    submit = SubmitField('Отпр.')