# -*- coding: utf-8 -*-


from app import db
from models.base import BaseMixin


class Follow(db.Model, BaseMixin):
    __tablename__ = 'follows'

    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
