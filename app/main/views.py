# -*- coding: utf-8 -*-


import json
import urllib.parse
import urllib.request

from flask import abort
from flask import current_app
from flask import flash
from flask import redirect, url_for
from flask import render_template
from flask import request
from flask_babel import gettext as _
from flask_login import current_user
from flask_login import login_required
from flask_sqlalchemy import get_debug_queries
from sqlalchemy import desc
from sqlalchemy.sql import func, and_
from werkzeug.contrib.atom import AtomFeed

from app import db, babel
from app.decorators import permission_required
from app.main import main
from app.main.forms import EditProfileForm, EditProfileAdminForm, ArticleForm, \
    CommentForm, WeatherForm
from models.article import Article
from models.category import Category
from models.comment import Comment
from models.role import Role, Permission
from models.user import User
from models.follow import Follow


@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(['en', 'zh_Hans_CN'])


@main.route('/', methods=['GET', 'POST'])
def index():
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['ARTICLES_PER_PAGE']
    pagination = Article.query\
        .outerjoin(Comment)\
        .group_by(Article.id)\
        .order_by(desc(func.count(Comment.id)))\
        .paginate(page, per_page=per_page, error_out=False)
    articles = pagination.items
    return render_template('index.html',
                           articles=articles,
                           endpoint='main.index',
                           categories_list=Category.get_categories(),
                           pagination=pagination)


@main.route('/all', methods=['GET', 'POST'])
def show_all_articles():
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['ARTICLES_PER_PAGE']
    pagination = Article.query\
        .order_by(Article.id.desc())\
        .paginate(page, per_page=per_page, error_out=False)
    articles = pagination.items
    return render_template('index.html',
                           articles=articles,
                           endpoint='main.show_all_articles',
                           categories_list=Category.get_categories(),
                           pagination=pagination)


@main.route('/followed')
@login_required
def show_followed_articles():
    if current_user.is_authenticated:
        page = request.args.get('page', 1, type=int)
        per_page = current_app.config['ARTICLES_PER_PAGE']
        pagination = current_user.followed_articles\
            .order_by(Article.id.desc())\
            .paginate(page, per_page=per_page, error_out=False)
        articles = pagination.items
        return render_template('index.html',
                               endpoint='main.show_followed_articles',
                               articles=articles,
                               categories_list=Category.get_categories(),
                               pagination=pagination)
    return redirect(url_for('.index'))


@main.route('/category/<string:category_name>', methods=['GET', 'POST'])
def show_category_articles(category_name):
    category_id = Category.query.filter_by(name=category_name).first().id
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['ARTICLES_PER_PAGE']
    pagination = Article.query\
        .join(Category, Article.category_id == Category.id)\
        .filter(Category.id == category_id)\
        .order_by(Article.id.desc())\
        .paginate(page, per_page=per_page, error_out=False)
    articles = pagination.items
    return render_template('index.html',
                           articles=articles,
                           endpoint='main.show_category_articles',
                           category_name=category_name,
                           categories_list=Category.get_categories(),
                           pagination=pagination)


@main.route('/tag/<string:tag>', methods=['GET', 'POST'])
def show_tag_articles(tag):
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['ARTICLES_PER_PAGE']
    pagination = Article.query\
        .filter(Article.tags.like('%' + tag + '%'))\
        .order_by(Article.id.desc())\
        .paginate(page, per_page=per_page, error_out=False)
    articles = pagination.items
    return render_template('index.html',
                           articles=articles,
                           endpoint='main.show_tag_articles',
                           tag=tag,
                           categories_list=Category.get_categories(),
                           pagination=pagination)


@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    followed_count = Follow.query.filter_by(follower_id=user.id, enable=True).count()
    followers_count = Follow.query.filter_by(followed_id=user.id, enable=True).count()
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['ARTICLES_PER_PAGE']
    pagination = user.articles\
        .order_by(Article.id.desc())\
        .paginate(page, per_page=per_page, error_out=False)
    articles = pagination.items
    return render_template('user/user.html',
                           user=user,
                           followed_count=followed_count,
                           followers_count=followers_count,
                           articles=articles,
                           pagination=pagination)


@main.route('/user/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.real_name = form.real_name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        db.session.commit()
        flash(_('Your profile has been updated'), 'success')
        return redirect(url_for('main.user', username=current_user.username))

    form.real_name.data = current_user.real_name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('user/edit_profile.html', form=form)


@main.route('/user/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.MODERATE_USER)
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.real_name = form.real_name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        db.session.commit()
        flash(_('The profile has been updated'), 'success')
        return redirect(url_for('main.user', username=user.username))

    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.real_name.data = user.real_name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('user/edit_profile.html', form=form, user=user)


@main.route('/publish-article', methods=['GET', 'POST'])
@login_required
def publish_article():
    form = ArticleForm()
    if current_user.can(Permission.WRITE_ARTICLE) and \
            form.validate_on_submit():
        title = form.title.data
        category = Category.query.get(form.category.data)
        tags = form.tags.data
        body = form.body.data
        article = Article(title=title,
                          category=category,
                          tags=tags,
                          body=body,
                          author=current_user._get_current_object())
        db.session.add(article)
        db.session.commit()
        return redirect(url_for('main.show_all_articles'))
    return render_template('article/publish_article.html', form=form, user=user)


@main.route('/edit-article/<int:id>', methods=['GET', 'POST'])
def edit_article(id):
    article = Article.query.get_or_404(id)
    if current_user != article.author and \
            not current_user.can(Permission.MODERATE_ARTICLE):
        abort(403)

    form = ArticleForm()
    if form.validate_on_submit():
        article.title = form.title.data
        article.category = Category.query.get(form.category.data)
        article.tags = form.tags.data
        article.body = form.body.data
        db.session.add(article)
        db.session.commit()
        flash(_('The article has been updated'), 'success')
        return redirect(url_for('main.article', id=article.id))

    form.title.data = article.title
    form.category.data = article.category_id
    form.tags.data = article.tags
    form.body.data = article.body
    return render_template('article/edit_article.html', form=form)


@main.route('/follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(_('Invalid user'), 'warning')
        return redirect(url_for('main.index'))

    if current_user.is_following(user):
        flash(_('You are already following this user'), 'info')
        return redirect(url_for('main.user', username=username))

    current_user.follow(user)
    flash(_('You are now following') + '%s' % username, 'info')
    return redirect(url_for('.user', username=username))


@main.route('/unfollow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(_('Invalid user'), 'warning')
        return redirect(url_for('main.index'))

    if not current_user.is_following(user):
        flash(_('You are not following this user'), 'info')
        return redirect(url_for('main.user', username=username))

    current_user.unfollow(user)
    flash(_('Your are not following %(username)s anymore', username=username), 'info')
    return redirect(url_for('main.user', username=username))


@main.route('/followers/<username>')
def followers(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(_('Invalid user'), 'warning')
        return redirect(url_for('main.index'))

    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['FOLLOWERS_PER_PAGE']
    pagination = Follow.query.with_entities(Follow, User)\
        .join(User, User.id == Follow.follower_id)\
        .filter(Follow.followed_id == user.id,
                Follow.enable == True)\
        .order_by(Follow.id.desc())\
        .paginate(page, per_page=per_page, error_out=False)
    follows = [{
        'user': item.User,
        'create_datetime': item.Follow.create_datetime
    } for item in pagination.items]
    return render_template('user/followers.html',
                           user=user,
                           title=_('\'s followers'),
                           endpoint='main.followers',
                           pagination=pagination,
                           follows=follows)


@main.route('/followed-by/<username>')
def followed_by(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(_('Invalid user'), 'warning')
        return redirect(url_for('main.index'))

    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['FOLLOWERS_PER_PAGE']
    pagination = Follow.query.with_entities(Follow, User)\
        .join(User, User.id == Follow.followed_id)\
        .filter(Follow.follower_id == user.id,
                Follow.enable == True)\
        .order_by(Follow.id.desc())\
        .paginate(page, per_page=per_page, error_out=False)
    follows = [{
        'user': item.User,
        'create_datetime': item.Follow.create_datetime
    } for item in pagination.items]
    return render_template('user/followers.html',
                           user=user,
                           title=_(' has followed'),
                           endpoint='main.followers',
                           pagination=pagination,
                           follows=follows)


@main.route('/article/<int:id>', methods=['GET', 'POST'])
def article(id):
    article = Article.query.get_or_404(id)
    prev_article = Article.query\
        .filter(and_(Article.author_id == article.author_id,
                     Article.create_datetime < article.create_datetime))\
        .order_by(Article.id.desc())\
        .first()
    next_article = Article.query\
        .filter(and_(Article.author_id == article.author_id,
                     Article.create_datetime > article.create_datetime))\
        .order_by(Article.id.asc())\
        .first()

    if request.method == 'GET':
        article.read_count += 1
    db.session.commit()
    form = CommentForm()

    if form.validate_on_submit():
        comment = Comment(body=form.body.data,
                          article=article,
                          author=current_user._get_current_object())
        db.session.add(comment)
        db.session.commit()
        flash(_('Your comment has been published'), 'success')
        return redirect(url_for('main.article', id=article.id, page=-1))

    page = request.args.get('page', 1, type=int)
    if page == -1:
        page = ((article.comments.count() - 1) //
                current_app.config['COMMENTS_PER_PAGE'] + 1)
    per_page = current_app.config['COMMENTS_PER_PAGE']
    pagination = article.comments\
        .order_by(Comment.id.asc())\
        .paginate(page, per_page=per_page, error_out=False)
    comments = pagination.items
    return render_template('article/article.html',
                           articles=[article],
                           prev_article=prev_article,
                           next_article=next_article,
                           form=form,
                           comments=comments,
                           pagination=pagination)


@main.route('/moderate')
@login_required
@permission_required(Permission.MODERATE_COMMENT)
def moderate():
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['COMMENTS_PER_PAGE']
    pagination = Comment.query\
        .order_by(Comment.id.desc())\
        .paginate(page, per_page=per_page, error_out=False)
    comments = pagination.items
    return render_template('moderate.html',
                           comments=comments,
                           pagination=pagination,
                           page=page)


@main.route('/moderate/enable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENT)
def moderate_enable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = False
    db.session.add(comment)
    db.session.commit()
    page = request.args.get('page', 1, type=int)
    return redirect(url_for('main.moderate', page=page))


@main.route('/moderate/disable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENT)
def moderate_disable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = True
    db.session.add(comment)
    db.session.commit()
    page = request.args.get('page', 1, type=int)
    return redirect(url_for('main.moderate', page=page))


@main.route('/about')
def about():
    return render_template('about.html')


@main.route('/weather_forecast', methods=['GET', 'POST'])
def weather_forecast():
    form = WeatherForm()
    if form.validate_on_submit():
        city = form.city.data
        param = urllib.parse.urlencode({
            'cityname': city,
            'dtype': current_app.config['JUHE_DATA_TYPE'],
            'format': current_app.config['JUHE_DATA_FORMAT'],
            'key': current_app.config['JUHE_API_KEY']
        })
        url = current_app.config['JUHE_WEATHER_URL'] + '?' + param
        result = json.loads(urllib.request.urlopen(url).read().decode('utf-8'))
        if result['error_code'] != 0:
            reason = result['reason']
            return render_template('weather.html', reason=reason)
        else:
            city = result['result']['today']['city']
            date = result['result']['today']['date_y']
            weather = result['result']['today']['weather']
            return render_template('weather.html',
                                   city=city,
                                   date=date,
                                   weather=weather)
    return render_template('weather_forecast.html', form=form)


@main.route('/tags_string')
def tags_string():
    return Article.string_from_tags()


@main.route('/feed')
def recent_feed():
    feed = AtomFeed('Recent Articles',
                    feed_url=request.url,
                    url=request.url_root)
    articles = Article.query.order_by(Article.id.desc()).limit(15).all()
    for article in articles:
        feed.add(article.title,
                 article.body_html,
                 content_type='html',
                 author=article.author.username,
                 url=url_for('main.article', id=article.id, _external=True),
                 updated=article.update_datetime)
    return feed.get_response()


@main.route('/search', methods=['GET', 'POST'])
def search():
    keyword = request.form.get('keyword')
    if not keyword:
        return redirect(url_for('main.index'))
    articles = Article.query.all()
    results = [article for article in articles
               if keyword in article.title or keyword in article.body]
    return render_template('search_result.html',
                           articles=results,
                           num_articles = len(results),
                           keyword=keyword)


@main.route('/upload-avatar', methods=['POST'])
def upload_avatar():
    pass


@main.after_app_request
def after_request(response):
    for query in get_debug_queries():
        if query.duration >= current_app.config['DB_QUERY_TIMEOUT']:
            current_app.logger.warning('Slow query: {}\n'
                                       'Parameters: {}\n'
                                       'Duration: %{:f}\n'
                                       'Context: {}\n'
                                       .format(query.statement,
                                               query.parameters,
                                               query.duration,
                                               query.context))
    return response
