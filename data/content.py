import sqlalchemy

from sqlalchemy import orm
from .db_session import SqlAlchemyBase
from flask_login import UserMixin


class Content(SqlAlchemyBase, UserMixin):
    __tablename__ = 'user_content'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True,
                           autoincrement=True)
    music_name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    music_author = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    url_music = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    url_img = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
    user = orm.relation('User')