import sqlalchemy

from sqlalchemy import orm
from .db_session import SqlAlchemyBase
from flask_login import UserMixin


# Таблица комментариев
class Comments(SqlAlchemyBase, UserMixin):
    __tablename__ = 'comments'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True,
                           autoincrement=True)
    text = sqlalchemy.Column(sqlalchemy.String)
    user_name = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.name'))
    user = orm.relation('User')
    content_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('user_content.id'))
    content = orm.relation('Content')