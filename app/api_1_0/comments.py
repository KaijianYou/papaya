# -*- coding: utf-8 -*-



from flask import jsonify
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
    comments = Comment.query.all()
    return jsonify({'comments': [comment.to_json() for comment in comments]})


@api.route('/comments/<int:id>')
def get_comment(id):
    comment = Comment.query.get_or_404(id)
    return jsonify(comment.to_json())


@api.route('/posts/<int:id>/comments/')
def get_post_comments(id):
    post = Post.query.get_or_404(id)
    comments = post.comments.all()
    return jsonify({'comments': [comment.to_json() for comment in comments]})


@api.route('/posts/<int:id>/comments/', methods=['POST'])
@permission_required(Permission.COMMENT)
def new_post_comments(id):
    post = Post.query.get_or_404(id)
    comment = Comment.from_json(request.json)
    comment.author = g.current_user
    comment.post = post
    db.session.add(comment)
    db.session.commit()
    return jsonify(comment.to_json()), 201, \
           {'Location': url_for('api.get_comment', id=comment.id, _external=True)}