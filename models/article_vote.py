# -*- coding: utf-8 -*-


from app import db
from models.base import BaseMixin


class VoteType(object):
    UP = 1
    DOWN = 2

class ArticleVote(db.Model, BaseMixin):
    __tablename__ = 'article_votes'

    voter_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    article_id = db.Column(db.Integer, db.ForeignKey('articles.id'))
    type = db.Column(db.Integer)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
