# -*- coding: utf-8 -*-


from datetime import datetime

from flask import url_for

from app import db


class Comment(db.Model):

    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(200))
    create_timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    disabled = db.Column(db.Boolean, default=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))

    def to_json(self):
        comment_json = {
            'url': url_for('api.get_comment', id=self.id, _external=True),
            'body': self.body,
            'create_timestamp': self.create_timestamp,
            'author': url_for('api.get_user', id=self.author_id, _external=True),
            'post': url_for('api.get_post', id=self.post_id, _external=True),
        }
        return comment_json

    @staticmethod
    def from_json(comment_json):
        body = comment_json.get('body')
        if not body:
            raise ValueError('comment does not have a body')
        return Comment(body=body)
