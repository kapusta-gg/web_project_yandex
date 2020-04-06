from flask_wtf import FlaskForm
from mongoengine import ImageField

from wtforms import StringField, FileField, SubmitField, ValidationError
from wtforms.validators import DataRequired, InputRequired


def validate_file_extension(value):
    ext = value.name
    valid_extensions = ['.jpg', '.png']
    if not ext.lower() in valid_extensions:
        raise ValidationError('Unsupported file extension.')


class MakerForm(FlaskForm):
    author_name = StringField('Имя автора произведения:', validators=[DataRequired()])
    song_name = StringField('Название песни:', validators=[DataRequired()])
    image = FileField('Загрузите картинку', validators=[InputRequired()])
    music = FileField('Загрузите музыку', validators=[InputRequired()])
    submit = SubmitField('Готово!')
