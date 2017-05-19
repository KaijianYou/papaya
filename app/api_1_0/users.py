# -*- coding: utf-8 -*-


from flask import jsonify

from app.api_1_0 import api
from app.models import User


@api.route('/users/<int:id>')
def get_user(id):
    user = User.query.get_or_404(id)
    return jsonify(user.to_json())


@api.route('/users/')
def get_users():
    users = User.query.all()
    return jsonify({'users': [user.to_json() for user in users]})


@api.route('/users/<int:id>/posts/')
def get_user_posts(id):
    user = User.query.get_or_404(id)
    posts = user.posts.all()
    return jsonify({'posts': [post.to_json() for post in posts]})


@api.route('/users/<int:id>/followed/posts/')
def get_user_followed_posts(id):
    user = User.query.get_or_404(id)
    posts = user.followed_posts()
    return jsonify({'posts': [post.to_json() for post in posts]})
