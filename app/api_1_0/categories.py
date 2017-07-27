# -*- coding: utf-8 -*-


from flask import jsonify

from app.api_1_0 import api
from models.category import Category


@api.route('/categories/<int:id>')
def get_category(id):
    category = Category.query.get_or_404(id)
    return jsonify(category.to_json())


@api.route('/categories/')
def get_categories():
    categories = Category.query.all()
    return jsonify({
        'categories': [category.to_json() for category in categories]
    })


@api.route('/categories/<int:id>/posts/')
def get_categories_posts(id):
    category = Category.query.get_or_404(id)
    posts = category.posts.all()
    return jsonify({
        'posts': [post.to_json() for post in posts]
    })
