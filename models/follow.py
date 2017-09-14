# -*- coding: utf-8 -*-


from datetime import datetime

from app import db


class Follow(db.Model):
    __tablename__ = 'follows'

    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    create_datetime = db.Column(db.DateTime, default=datetime.utcnow)
