# -*- coding: utf-8 -*-


from app import db
from models.base import BaseMixin


class CollectionType(object):
    """收藏类型"""
    ARTICLE = 1  # 文章


class Collections(db.Model, BaseMixin):
    """用户收藏表"""
    __tablename__ = 'collections'

    owner_id = db.Column(db.Integer, index=True)
    item_id = db.Column(db.Integer, index=True)
    type = db.Column(db.Integer)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
