# -*- coding: utf-8 -*-

from datetime import datetime

import bleach
from flask import url_for
from markdown import markdown

from app import db
from models.category import Category


class Post(db.Model):

    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64), index=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    tags = db.Column(db.String(200), nullable=False)
    body = db.Column(db.Text, nullable=False)
    body_html = db.Column(db.Text, nullable=False)
    create_timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    update_timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    comments = db.relationship('Comment', backref='post', lazy='dynamic')

    def __repr__(self):
        return '<Post %s>' % self.title

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul', 'h1',
                        'h2', 'h3', 'p', 'hr', 'br', 'img']
        attrs = {
            '*': ['class'],
            'a': ['href', 'rel'],
            'img': ['src', 'alt'],
        }
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, attributes=attrs, strip=True))

    def get_tags(self):
        tags_list = [tag for tag in self.tags.split(',') if tag]
        return tags_list

    @staticmethod
    def string_from_tags():
        posts = Post.query.all()
        tags_set = set()
        for post in posts:
            tags_set.update(set(post.get_tags()))
        tags_string = ' '.join(tags_set)
        return tags_string

    def get_category_name(self):
        return Category.query.get(self.category_id).name

    def to_json(self):
        post_json = {
            'url': url_for('api.get_post', id=self.id, _external=True),
            'title': self.title,
            'category': url_for('api.get_category', id=self.category_id, _external=True),
            'tags': self.get_tags(),
            'body': self.body,
            'body_html': self.body_html,
            'create_time': self.create_timestamp,
            'update_time': self.update_timestamp,
            'author': url_for('api.get_user', id=self.author_id, _external=True),
            'comments': url_for('api.get_post_comments', id=self.id, _external=True),
            'comment_count': self.comments.count(),
        }
        return post_json

    @staticmethod
    def from_json(post_json):
        title = post_json.get('title')
        if not title:
            raise ValueError('post does not have a title')
        category = post_json.get('category')
        if not category:
            raise ValueError('post does not have a category')
        if not Category.query.filter_by(name=category).first():
            raise ValueError('wrong category')
        tags = post_json.get('tags')
        if not tags:
            raise ValueError('post does not have tags')
        body = post_json.get('body')
        if not body:
            raise ValueError('post does not have a body')
        return Post(title=title, tags=tags, body=body)


# 当 Post 实例的 body 字段更新，on_changed_body 会被自动调用
db.event.listen(Post.body, 'set', Post.on_changed_body)
