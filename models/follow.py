from app import db
from models.base import BaseMixin


class Follow(db.Model, BaseMixin):
    __tablename__ = 'follows'

    follower_id = db.Column(db.Integer, index=True, nullable=True)
    followed_id = db.Column(db.Integer, index=True, nullable=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
