# -*- coding: utf-8 -*-


from flask import jsonify, request, current_app, url_for

from app.api_1_0 import api
from models.user import User
from models.post import Post


@api.route('/users/<int:id>')
def get_user(id):
    user = User.query.get_or_404(id)
    return jsonify(user.to_dict())


@api.route('/users/<int:id>/posts/')
def get_user_posts(id):
    user = User.query.get_or_404(id)
    page = request.args.get('page', default=1, type=int)
    pagination = user.posts.order_by(Post.create_timestamp.desc())\
        .paginate(page, per_page=current_app.config['POSTS_PER_PAGE'])
    posts = pagination.items

    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_user_posts', page=page-1, _external=True)
    next = None
    if pagination.has_next:
        next = url_for('api.get_user_posts', page=page-1, _external=True)
    return jsonify({
        'posts': [post.to_dict() for post in posts],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })


@api.route('/users/<int:id>/followed/posts/')
def get_user_followed_posts(id):
    user = User.query.get_or_404(id)
    page = request.args.get('page', default=1, type=int)
    pagination = user.followed_posts.order_by(Post.create_timestamp.desc())\
        .paginate(page, per_page=current_app.config['POSTS_PER_PAGE'])
    posts = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_user_followed_posts', page=page-1, _external=True)
    next = None
    if pagination.has_next:
        next = url_for('api.get_user_followed_posts', page=page-1, _external=True)
    return jsonify({
        'posts': [post.to_dict() for post in posts],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })
