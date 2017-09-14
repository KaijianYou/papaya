# -*- coding: utf-8 -*-


from flask import url_for

from app import db
from models.base import BaseMixin


class Category(db.Model, BaseMixin):
    __tablename__ = 'categories'

    name = db.Column(db.String(32), nullable=False, unique=True)
    articles = db.relationship('Article', backref='category', lazy='dynamic')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @staticmethod
    def insert_categories():
        categories_list = [
            '计算机与编程', '思考与感言', '读书与写作', '外语学习', '生活',
            '好玩有趣', '工作', '学习资料', '建议与反馈', '新闻资讯'
        ]
        for category_name in categories_list:
            category = Category.query.filter_by(name=category_name).first()
            if not category:
                category = Category(name=category_name)
                db.session.add(category)
        db.session.commit()

    @staticmethod
    def get_categories():
        categories = Category.query.all()
        categories_list = [(category.name, category.articles.count())
                           for category in categories]
        return categories_list

    def to_dict(self):
        return {
            'url': url_for('api.get_category', id=self.id, _external=True),
            'name': self.name,
            'articles': url_for('api.get_category_articles', id=self.id,  _external=True),
            'article_count': self.articles.count(),
        }
