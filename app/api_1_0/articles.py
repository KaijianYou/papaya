from flask import request, g, url_for, current_app, jsonify
from flask_babel import gettext as _

from app import db
from app.api_1_0 import api
from app.api_1_0.decorators import permission_required
from app.api_1_0.errors import forbidden, not_found
from models.article import Article
from models.role import Permission


@api.route('/articles/<int:id>')
def get_article(id):
    article = Article.query.get(id)
    if not article:
        return not_found(_('The article not exists'))
    return jsonify(article.to_dict())


@api.route('/articles/')
def get_articles():
    page = request.args.get('page', default=1, type=int)
    pagination = Article.query.order_by(Article.id.desc())\
        .paginate(page=page, per_page=current_app.config['ARTICLES_PER_PAGE'])
    articles = pagination.items

    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_articles', page=page-1, _external=True)
    next = None
    if pagination.has_next:
        next = url_for('api.get_articles', page=page+1, _external=True)

    return jsonify({
        'articles': [article.to_dict() for article in articles],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })


@api.route('/articles/', methods=['POST'])
@permission_required(Permission.WRITE_ARTICLE)
def new_article():
    article = Article.from_dict(request.json)
    article.author = g.current_user
    db.session.add(article)
    db.session.commit()
    return (
        jsonify(article.to_dict()),
        201,
        {'Location': url_for('api.get_article', id=article.id, _external=True)}
    )


@api.route('/articles/<int:id>', methods=['PUT'])
@permission_required(Permission.WRITE_ARTICLE)
def edit_article(id):
    article = Article.query.get(id)
    if not article:
        return not_found(_('The article not exists'))
    if g.current_user != article.author and \
            not g.current_user.can(Permission.MODERATE_ARTICLE):
        return forbidden('permission denied')
    article = Article.from_dict(request.json)
    db.session.add(article)
    db.session.commit()
    return jsonify(article.to_dict())
