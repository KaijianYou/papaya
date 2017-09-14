# -*- coding: utf-8 -*-


from flask import jsonify, request, current_app, url_for
from flask_babel import gettext as _

from app.api_1_0 import api
from models.user import User
from models.article import Article
from app.api_1_0.errors import not_found


@api.route('/users/<int:id>')
def get_user(id):
    user = User.query.get(id)
    if not user:
        return not_found(_('The user not exists'))
    return jsonify(user.to_dict())


@api.route('/users/<int:id>/articles/')
def get_user_articles(id):
    user = User.query.get(id)
    if not user:
        return not_found(_('The user not exists'))

    page = request.args.get('page', default=1, type=int)
    pagination = user.articles.order_by(Article.id.desc())\
        .paginate(page, per_page=current_app.config['ARTICLES_PER_PAGE'])
    articles = pagination.items

    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_user_articles', page=page-1, _external=True)
    next = None
    if pagination.has_next:
        next = url_for('api.get_user_articles', page=page-1, _external=True)
    return jsonify({
        'articles': [article.to_dict() for article in articles],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })


@api.route('/users/<int:id>/followed/articles/')
def get_user_followed_articles(id):
    user = User.query.get(id)
    if not user:
        return not_found('The user not exists')
    page = request.args.get('page', default=1, type=int)
    pagination = user.followed_articles.order_by(Article.id.desc())\
        .paginate(page, per_page=current_app.config['ARTICLES_PER_PAGE'])
    articles = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_user_followed_articles', page=page-1, _external=True)
    next = None
    if pagination.has_next:
        next = url_for('api.get_user_followed_articles', page=page-1, _external=True)
    return jsonify({
        'articles': [article.to_dict() for article in articles],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })
