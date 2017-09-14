# -*- coding: utf-8 -*-


from flask import jsonify, request, current_app, url_for
from flask_babel import gettext as _

from app.api_1_0 import api
from app.api_1_0.errors import not_found
from models.category import Category
from models.article import Article


@api.route('/categories/<int:id>')
def get_category(id):
    category = Category.query.get(id)
    if not category:
        return not_found(_('The category not exists'))
    return jsonify(category.to_dict())


@api.route('/categories/')
def get_categories():
    categories = Category.query.all()
    return jsonify({
        'categories': [category.to_dict() for category in categories]
    })


@api.route('/categories/<int:id>/articles/')
def get_categories_articles(id):
    category = Category.query.get(id)
    if not category:
        return not_found(_('The category not exists'))
    page = request.args.get('page', default=1, type=int)
    pagination = category.articles.order_by(Article.create_datetime.desc())\
        .paginate(page=page, per_page=current_app.config['ARTICLES_PER_PAGE'])
    articles = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_categories_articles', id=id, page=page-1, _external=True)
    next = None
    if pagination.has_next:
        next = url_for('api.get_categories_articles', id=id, page=page+1, _external=True)
    return jsonify({
        'articles': [article.to_dict() for article in articles],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })
