# -*- coding: utf-8 -*-



from flask import jsonify, current_app
from flask import request, g
from flask import url_for

from app import db
from app.api_1_0 import api
from app.api_1_0.decorators import permission_required
from models.post import Post
from models.comment import Comment
from models.role import Permission


@api.route('/comments/')
def get_comments():
    page = request.args.get('page', default=1, type=int)
    pagination = Comment.query.order_by(Comment.create_timestamp.desc())\
        .paginate(page, per_page=current_app.config['COMMENTS_PER_PAGE'])
    comments = pagination.items

    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_comments', page=page-1, _external=True)
    next = None
    if pagination.has_next:
        next = url_for('api.get_comments', page=page+1, _external=True)

    return jsonify({
        'comments': [comment.to_dict() for comment in comments],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })


@api.route('/comments/<int:id>')
def get_comment(id):
    comment = Comment.query.get_or_404(id)
    return jsonify(comment.to_dict())


@api.route('/posts/<int:id>/comments/')
def get_post_comments(id):
    post = Post.query.get_or_404(id)
    page = request.args.get('page', default=1, type=int)
    pagination = post.comments.order_by(Comment.create_timestamp.asc())\
        .paginate(page, per_page=current_app.config['COMMENTS_PER_PAGE'])
    comments = pagination.items

    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_post_comments', id=id, page=page-1, _external=True)
    next = None
    if pagination.has_next:
        next = url_for('api.get_post_comments', id=id, page=page+1, _external=True)

    return jsonify({
        'comments': [comment.to_dict() for comment in comments],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })


@api.route('/posts/<int:id>/comments/', methods=['POST'])
@permission_required(Permission.COMMENT)
def new_post_comments(id):
    post = Post.query.get_or_404(id)
    comment = Comment.from_dict(request.json)
    comment.author = g.current_user
    comment.post = post
    db.session.add(comment)
    db.session.commit()

    return (
        jsonify(comment.to_dict()),
        201,
        {'Location': url_for('api.get_comment', id=comment.id, _external=True)}
    )