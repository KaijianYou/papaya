# -*- coding: utf-8 -*-


from flask import request, g, url_for, current_app, jsonify

from app import db
from app.api_1_0 import api
from app.api_1_0.decorators import permission_required
from app.api_1_0.errors import forbidden
from models.post import Post
from models.role import Permission


@api.route('/posts/<int:id>')
def get_post(id):
    post = Post.query.get_or_404(id)
    return jsonify(post.to_dict())


@api.route('/posts/')
def get_posts():
    page = request.args.get('page', default=1, type=int)
    pagination = Post.query.order_by(Post.create_timestamp.desc())\
        .paginate(page=page, per_page=current_app.config['POSTS_PER_PAGE'])
    posts = pagination.items

    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_posts', page=page-1, _external=True)
    next = None
    if pagination.has_next:
        next = url_for('api.get_posts', page=page+1, _external=True)

    return jsonify({
        'posts': [post.to_dict() for post in posts],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })


@api.route('/posts/', methods=['POST'])
@permission_required(Permission.WRITE_ARTICLES)
def new_post():
    post = Post.from_dict(request.json)
    post.author = g.current_user
    db.session.add(post)
    db.session.commit()
    return (
        jsonify(post.to_dict()),
        201,
        {'Location': url_for('api.get_post', id=post.id, _external=True)}
    )


@api.route('/posts/<int:id>', methods=['PUT'])
@permission_required(Permission.WRITE_ARTICLES)
def edit_post(id):
    post = Post.query.get_or_404(id)
    if g.current_user != post.author and \
            not g.current_user.can(Permission.ADMINISTER):
        return forbidden('permission denied')
    post = Post.from_dict(request.json)
    db.session.add(post)
    db.session.commit()
    return jsonify(post.to_dict())
