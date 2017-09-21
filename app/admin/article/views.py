# -*- coding: utf-8 -*-


from flask import render_template, request, current_app
from app.admin import admin
from models.article import Article
from models.category import Category


@admin.route('/articles')
def article_list():
    page = request.args.get('page', default=1, type=int)
    per_page = current_app.config['ARTICLES_PER_PAGE']
    pagination = Article.query.paginate(page, per_page, error_out=False)
    articles = pagination.items
    return render_template('article_list.html',
                           articles=articles,
                           pagination=pagination)


@admin.route('/categories')
def category_list():
    page = request.args.get('page', default=1, type=int)
    per_page = current_app.config['CATEGORY_PER_PAGE']
    pagination = Category.query.paginate(page, per_page, error_out=False)
    categories = pagination.items
    return render_template('category_list.html',
                           categories=categories,
                           pagination=pagination)
