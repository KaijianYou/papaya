from flask import url_for

from app import db
from models.base import BaseMixin


class Comment(db.Model, BaseMixin):
    __tablename__ = 'comments'

    body = db.Column(db.String(200))
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    article_id = db.Column(db.Integer, db.ForeignKey('articles.id'))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def to_dict(self):
        return {
            'url': url_for('api.get_comment', id=self.id, _external=True),
            'body': self.body,
            'create_datetime': self.create_datetime,
            'author': url_for('api.get_user', id=self.author_id, _external=True),
            'article': url_for('api.get_article', id=self.article_id, _external=True),
        }

    @staticmethod
    def from_dict(comment_dict):
        body = comment_dict.get('body')
        if not body:
            raise ValueError('comment does not have a body')
        return Comment(body=body)
