# -*- coding: utf-8 -*-


from flask import render_template
from flask import flash
from flask import jsonify
from flask import abort
from flask import redirect, url_for
from flask import request
from flask import current_app
from flask_login import login_required
from flask_login import current_user
from flask_sqlalchemy import get_debug_queries
from sqlalchemy import desc
from sqlalchemy.sql import func
from flask_babel import gettext as _

from app import db, babel
from . import main
from .forms import EditProfileForm, EditProfileAdminForm
from .forms import PostForm, CommentForm
from ..models import User, Role, Permission, Post, Comment, Category
from ..decorators import admin_required
from ..decorators import permission_required


@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(['en', 'zh_Hans_CN'])


# 如果不指定 methods 参数，则默认将函数注册为 GET 请求的处理程序
@main.route('/', methods=['GET', 'POST'])
def index():
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.outerjoin(Comment)\
        .group_by(Post.id).order_by(desc(func.count(Comment.id))).paginate(
        page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)
    posts = pagination.items
    return render_template('index.html',
                           posts=posts,
                           endpoint='main.index',
                           categories_list=Category.get_categories(),
                           show_followed_posts=show_followed_posts,
                           show_post_body=False,
                           pagination=pagination)


@main.route('/all', methods=['GET', 'POST'])
def show_all_posts():
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.create_timestamp.desc()).paginate(
        page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)
    posts = pagination.items
    return render_template('index.html',
                           posts=posts,
                           endpoint='main.show_all_posts',
                           categories_list=Category.get_categories(),
                           show_post_body=False,
                           pagination=pagination)


@main.route('/followed')
@login_required
def show_followed_posts():
    if current_user.is_authenticated:
        query = current_user.followed_posts()
        page = request.args.get('page', 1, type=int)
        pagination = query.order_by(Post.create_timestamp.desc()).paginate(
            page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)
        posts = pagination.items
        return render_template('index.html',
                               endpoint='main.show_followed_posts',
                               posts=posts,
                               categories_list=Category.get_categories(),
                               show_post_body=False,
                               pagination=pagination)
    return redirect(url_for('.index'))


@main.route('/category/<string:category_name>', methods=['GET', 'POST'])
def category(category_name):
    category_id = Category.query.filter_by(name=category_name).first().id
    posts = Post.query.join(Category, Post.category_id == Category.id)\
        .filter(Category.id == category_id)
    page = request.args.get('page', 1, type=int)
    pagination = posts.order_by(Post.create_timestamp.desc()).paginate(
        page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)
    posts = pagination.items
    return render_template('index.html',
                           posts=posts,
                           endpoint='main.category',
                           category_name=category_name,
                           categories_list=Category.get_categories(),
                           show_post_body=False,
                           pagination=pagination)


@main.route('/tag/<string:tag_name>', methods=['GET', 'POST'])
def tag(tag_name):
    posts = Post.query.filter(Post.tags.like('%' + tag_name + '%'))
    page = request.args.get('page', 1, type=int)
    pagination = posts.order_by(Post.create_timestamp.desc()).paginate(
        page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)
    posts = pagination.items
    return render_template('index.html',
                           posts=posts,
                           endpoint='main.tag',
                           tag_name=tag_name,
                           categories_list=Category.get_categories(),
                           show_post_body=False,
                           pagination=pagination)


@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    pagination = user.posts.order_by(Post.create_timestamp.desc()).paginate(
        page, per_page=current_app.config['POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    return render_template('user.html', user=user, posts=posts,
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
        return redirect(url_for('.user', username=current_user.username))
    form.real_name.data = current_user.real_name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)


@main.route('/user/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
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
        return redirect(url_for('.user', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.real_name.data = user.real_name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('edit_profile.html', form=form, user=user)


@main.route('/publish-post', methods=['GET', 'POST'])
@login_required
def publish_post():
    form = PostForm()
    if current_user.can(Permission.WRITE_ARTICLES) and \
            form.validate_on_submit():
        title = form.title.data
        category = Category.query.get(form.category.data)
        tags = form.tags.data
        body = form.body.data
        print(type(current_user._get_current_object()))
        post = Post(title=title,
                    category=category,
                    tags=tags,
                    body=body,
                    author=current_user._get_current_object())
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('.index'))
    return render_template('publish_post.html', form=form, user=user)


@main.route('/edit-post/<int:id>', methods=['GET', 'POST'])
def edit_post(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author and \
            not current_user.can(Permission.ADMINISTER):
        abort(403)

    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.category = Category.query.get(form.category.data)
        post.tags = form.tags.data
        post.body = form.body.data
        db.session.add(post)
        db.session.commit()
        flash(_('The post has been updated'), 'success')
        return redirect(url_for('.post', id=post.id))
    form.title.data = post.title
    form.category.data = post.category_id
    form.tags.data = post.tags
    form.body.data = post.body
    return render_template('edit_post.html', form=form)


@main.route('/follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(_('Invalid user'), 'warning')
        return redirect(url_for('.index'))
    if current_user.is_following(user):
        flash(_('You are already following this user'), 'info')
        return redirect(url_for('.user', username=username))
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
        return redirect(url_for('.index'))
    if not current_user.is_following(user):
        flash(_('You are not following this user'), 'info')
        return redirect(url_for('.user', username=username))
    current_user.unfollow(user)
    flash(_('Your are not following %(username)s anymore', username=username), 'info')
    return redirect(url_for('.user', username=username))


@main.route('/followers/<username>')
def followers(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(_('Invalid user'), 'warning')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followers.paginate(
        page, per_page=current_app.config['FOLLOWERS_PER_PAGE'], error_out=False)
    follows = [{'user': item.follower, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('followers.html', user=user, title=_('\'s followers'),
                           endpoint='.followers', pagination=pagination,
                           follows=follows)


@main.route('/followed-by/<username>')
def followed_by(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(_('Invalid user'), 'warning')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followed.paginate(
        page, per_page=current_app.config['FOLLOWERS_PER_PAGE'], error_out=False)
    follows = [{'user': item.followed, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('followers.html', user=user, title=_(' has followed'),
                           endpoint='.followers', pagination=pagination,
                           follows=follows)


@main.route('/post/<int:id>', methods=['GET', 'POST'])
def post(id):
    post = Post.query.get_or_404(id)
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(body=form.body.data, post=post,
                          author=current_user._get_current_object())
        db.session.add(comment)
        db.session.commit()
        flash(_('Your comment has been published'), 'success')
        return redirect(url_for('.post', id=post.id, page=-1))

    page = request.args.get('page', 1, type=int)
    if page == -1:
        page = (post.comments.count() - 1) // \
               current_app.config['COMMENTS_PER_PAGE'] + 1
    pagination = post.comments.order_by(Comment.timestamp.asc()).paginate(
        page, per_page=current_app.config['COMMENTS_PER_PAGE'], error_out=False)
    comments = pagination.items
    return render_template('post.html', posts=[post], form=form,
                           show_post_body=True, comments=comments,
                           pagination=pagination)


@main.route('/moderate')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate():
    page = request.args.get('page', 1, type=int)
    pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(
        page, per_page=current_app.config['COMMENTS_PER_PAGE'], error_out=False)
    comments = pagination.items
    return render_template('moderate.html', comments=comments,
                           pagination=pagination, page=page)


@main.route('/moderate/enable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_enable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = False
    db.session.add(comment)
    db.session.commit()
    page = request.args.get('page', 1, type=int)
    return redirect(url_for('.moderate', page=page))


@main.route('/moderate/disable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_disable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = True
    db.session.add(comment)
    db.session.commit()
    page = request.args.get('page', 1, type=int)
    return redirect(url_for('.moderate', page=page))


@main.route('/about')
def about():
    return render_template('about.html')


@main.route('/_get_tags_string')
def get_tags_string():
    return Post.get_tags_string()


@main.after_app_request
def after_request(response):
    for query in get_debug_queries():
        if query.duration >= current_app.config['DB_QUERY_TIMEOUT']:
            current_app.logger.warning(
                'Slow query: %s\nParameters: %s\nDuration: %fs\nContext: %s\n' %
                (query.statement, query.parameters, query.duration, query.context))
    return response
