# -*- coding: utf-8 -*-


import bleach
from flask import url_for
from markdown import markdown

from app import db
from models.base import BaseMixin
from models.category import Category


class Article(db.Model, BaseMixin):
    __tablename__ = 'articles'

    title = db.Column(db.String(64), index=True)
    tags = db.Column(db.String(200), nullable=False)
    body = db.Column(db.Text, nullable=False)
    body_html = db.Column(db.Text)
    read_count = db.Column(db.Integer, default=0)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    votes = db.relationship('ArticleVote', backref='article', lazy='dynamic')
    comments = db.relationship('Comment', backref='article', lazy='dynamic')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = [
            'a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
            'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul', 'h1',
            'h2', 'h3', 'p', 'hr', 'br', 'img'
        ]
        attributes = {
            '*': ['class'],
            'a': ['href', 'rel'],
            'img': ['src', 'alt'],
        }
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, attributes=attributes, strip=True))

    def get_tags(self):
        tags_list = [tag for tag in self.tags.split(',') if tag]
        return tags_list

    @classmethod
    def string_from_tags(cls):
        posts = cls.query.all()
        tags_set = set()
        for post in posts:
            tags_set.update(set(post.get_tags()))
        tags_string = ' '.join(tags_set)
        return tags_string

    def get_category_name(self):
        return Category.query.get(self.category_id).name

    def to_dict(self):
        return {
            'url': url_for('api.get_post', id=self.id, _external=True),
            'title': self.title,
            'category': url_for('api.get_category', id=self.category_id, _external=True),
            'tags': self.get_tags(),
            'body': self.body,
            'body_html': self.body_html,
            'create_datetime': self.create_datetime,
            'update_datetime': self.update_datetime,
            'read_count': self.read_count,
            'upvote_count': self.upvote_count,
            'downvote_count': self.downvote_count,
            'author': url_for('api.get_user', id=self.author_id, _external=True),
            'comments': url_for('api.get_post_comments', id=self.id, _external=True),
            'comment_count': self.comments.count(),
        }

    @staticmethod
    def from_dict(article_dict):
        title = article_dict.get('title')
        if not title:
            raise ValueError('article does not have a title')
        category = article_dict.get('category')
        if not category:
            raise ValueError('article does not have a category')
        if not Category.query.filter_by(name=category).first():
            raise ValueError('wrong category')
        tags = article_dict.get('tags')
        if not tags:
            raise ValueError('post does not have tags')
        body = article_dict.get('body')
        if not body:
            raise ValueError('post does not have a body')
        return Article(title=title, tags=tags, body=body)


# 当 Post 实例的 body 字段更新，on_changed_body 会被自动调用
db.event.listen(Article.body, 'set', Article.on_changed_body)
