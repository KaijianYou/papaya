# -*- coding: utf-8 -*-


import hashlib
from datetime import datetime

from flask_login import UserMixin, AnonymousUserMixin
from flask import current_app
from flask import request
from flask import url_for
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from markdown import markdown
import bleach

from app import db
from app import login_manager


class Follow(db.Model):
    __tablename__ = 'follows'

    follower_id = db.Column(db.Integer,
                            db.ForeignKey('users.id'),
                            primary_key=True)
    followed_id = db.Column(db.Integer,
                            db.ForeignKey('users.id'),
                            primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class Permission:
    """
    # -------------------------------------------------------------------------
    # |        操  作        |      位  值       |         说  明             |
    # | 关注他人             | 0b00000001 (0x01) | 关注其他用户               |
    # | 在他人文章中发表评论 | 0b00000010 (0x02) | 在他人撰写的文章中发布评论 |
    # | 写文章               | 0b00000100 (0x04) | 写原创文章                 |
    # | 管理他人发表的评论   | 0b00001000 (0x08) | 查处他人发表的不当评论     |
    # | 管理员权限           | 0b10000000 (0x80) | 管理网站                   |
    # -------------------------------------------------------------------------    
    """
    FOLLOW = 0x01
    COMMENT = 0x02
    WRITE_ARTICLES = 0x04
    MODERATE_COMMENTS = 0x08
    ADMINISTER = 0x80


class Role(db.Model):
    """
    # --------------------------------------------------------------------------------
    # | 用户角色 |       权  限       |          说明                                |
    # | 匿名     | 0b00000000 (0x00)  | 未登录的用户。在程序中只有阅读权限           |
    # | 用户     | 0b00000111 (0x07)  | 具有发布文章、发表评论和关注其他用户的权限。 |
    # |          |                    | 这是新用户的默认角色                         |
    # | 协管员   | 0b00001111 (0x0f)  | 增加审查不当评论的权限                       |
    # | 管理员   | 0b11111111 (0xff)  | 具有所有权限，包括修改其他用户所属角色的权限 |
    # --------------------------------------------------------------------------------
    """
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<Role %s>' % self.name

    @staticmethod
    def insert_roles():
        roles = {
            'User':
                (Permission.FOLLOW |
                 Permission.COMMENT |
                 Permission.WRITE_ARTICLES, True),
            'Moderator':
                (Permission.FOLLOW |
                 Permission.COMMENT |
                 Permission.WRITE_ARTICLES |
                 Permission.MODERATE_COMMENTS, False),
            'Administrator':
                (0xff, False)
        }

        for role_name in roles:
            role = Role.query.filter_by(name=role_name).first()
            if role is None:
                role = Role(name=role_name)
            role.permissions = roles[role_name][0]
            role.default = roles[role_name][1]
            db.session.add(role)
        db.session.commit()


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(64), nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    role_id = db.Column('role_id', db.Integer, db.ForeignKey('roles.id'))
    real_name = db.Column(db.String(64))
    email = db.Column(db.String(64), unique=True, index=True, nullable=False)
    location = db.Column(db.String(64),)
    about_me = db.Column(db.Text())
    register_date = db.Column(db.DateTime(), default=datetime.utcnow)
    last_visited = db.Column(db.DateTime(), default=datetime.utcnow)
    confirmed = db.Column(db.Boolean, default=False)
    avatar_hash = db.Column(db.String(32))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    comments = db.relationship('Comment', backref='author', lazy='dynamic')
    followed = db.relationship('Follow', foreign_keys=[Follow.follower_id],
                               backref=db.backref('follower', lazy='joined'),
                               lazy='dynamic', cascade='all, delete-orphan')
    followers = db.relationship('Follow', foreign_keys=[Follow.followed_id],
                                backref=db.backref('followed', lazy='joined'),
                                lazy='dynamic', cascade='all, delete-orphan')

    @staticmethod
    def generate_fake(count=100):
        from sqlalchemy.exc import IntegrityError
        from random import seed
        import forgery_py

        seed()
        for i in range(count):
            user = User(email=forgery_py.internet.email_address(),
                        username=forgery_py.internet.user_name(True),
                        password=forgery_py.lorem_ipsum.word(),
                        confirmed=True,
                        real_name=forgery_py.name.full_name(),
                        location=forgery_py.address.city(),
                        about_me=forgery_py.lorem_ipsum.sentence(),
                        last_visited=forgery_py.date.date(True))
            db.session.add(user)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)

        if self.role is None:
            if self.email == current_app.config['ADMIN_EMAIL']:
                self.role = Role.query.filter_by(permissions=0xff).first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()

        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = hashlib.md5(self.email.encode('utf-8')).hexdigest()

        self.followed.append(Follow(followed=self))  # 把自己设为自己的关注者

    def __repr__(self):
        return '<User %s>' % self.username

    @property
    def password(self):
        raise AttributeError('password is not readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=60*60):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def generate_auth_token(self, expiration=60*60):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except Exception:
            return False
        return User.query.get(data['id'], None)

    @staticmethod
    def add_self_follows():
        for user in User.query.all():
            if not user.is_following(user):
                user.follow(user)
                db.session.add(user)
                db.session.commit()

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except Exception:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        db.session.commit()
        return True

    def generate_password_reset_token(self, expiration=60*60):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id})

    def reset_password(self, token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except Exception:
            return False
        if data.get('reset') != self.id:
            return False
        self.password = new_password
        db.session.add(self)
        db.session.commit()
        return True

    def generate_email_change_token(self, new_email, expiration=60*60):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'change_email': self.id, 'new_email': new_email})

    def change_email(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except Exception:
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        self.avatar_hash = hashlib.md5(self.email.encode('utf-8')).hexdigest()
        db.session.add(self)
        db.session.commit()
        return True

    def can(self, permissions):
        return self.role is not None and \
               (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    def update_last_visited(self):
        self.last_visited = datetime.utcnow()
        db.session.add(self)
        # db.session.commit()

    def get_avatar(self, size=100, default='identicon', rating='g'):
        """从 gravatar 网站获取头像"""
        if request.is_secure:
            url = 'http://secure.gravatar.com/avatar'
        else:
            url = 'http://www.gravatar.com/avatar'
        hash_code = hashlib.md5(self.email.encode('utf-8')).hexdigest()
        return '{url}/{hash_code}?s={size}&d={default}&r={rating}' \
            .format(url=url,
                    hash_code=hash_code,
                    size=size,
                    default=default,
                    rating=rating)

    def follow(self, user):
        if not self.is_following(user):
            f = Follow(follower=self, followed=user)
            db.session.add(f)
            db.session.commit()

    def unfollow(self, user):
        f = self.followed.filter_by(followed_id=user.id).first()
        if f:
            db.session.delete(f)
            db.session.commit()

    def is_following(self, user):
        return self.followed.filter_by(followed_id=user.id).first() is not None

    def is_followed_by(self, user):
        return self.followers.filter_by(follower_id=user.id).first() is not None

    def followed_posts(self):
        """获取已关注用户的文章"""
        return Post.query.join(Follow, Follow.followed_id == Post.author_id)\
            .filter(Follow.follower_id == self.id)

    def to_json(self):
        user_json = {
            'url': url_for('api.get_user', id=self.id, _external=True),
            'username': self.username,
            'about_me': self.about_me,
            'register_date': self.register_date,
            'last_visit': self.last_visited,
            'posts': url_for('api.get_user_posts', id=self.id, _external=True),
            'followed_posts': url_for('api.get_user_followed_posts', id=self.id,
                                      _external=True),
            'post_count': self.posts.count(),
        }
        return user_json


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False


login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), nullable=False, unique=True)
    posts = db.relationship('Post', backref='category', lazy='dynamic')

    def __repr__(self):
        return '<Category %s>' % self.name

    @staticmethod
    def insert_categories():
        categories_list = [
            '计算机与编程', '思考与感言', '读书与写作', '外语学习', '生活',
            '好玩有趣', '工作', '学习资料', '建议与反馈', '新闻资讯']
        for category_name in categories_list:
            category = Category.query.filter_by(name=category_name).first()
            if category is None:
                category = Category(name=category_name)
                db.session.add(category)
        db.session.commit()

    @staticmethod
    def get_categories():
        categories = Category.query.all()
        categories_list = [(category.name, category.posts.count())
                           for category in categories]
        return categories_list

    def to_json(self):
        category_json = {
            'url': url_for('api.get_category', id=self.id, _external=True),
            'name': self.name,
            # 'posts': url_for('api.get_category_posts', id=self.id,
            #                  _external=True),
            'post_count': self.posts.count(),
        }
        return category_json


class Post(db.Model):
    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64), index=True)
    category_id = db.Column(db.Integer,
                            db.ForeignKey('categories.id'),
                            nullable=False)
    tags = db.Column(db.String(200), nullable=False)
    body = db.Column(db.Text, nullable=False)
    body_html = db.Column(db.Text, nullable=False)
    create_timestamp = db.Column(db.DateTime,
                                 index=True,
                                 default=datetime.utcnow)
    update_timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    author_id = db.Column(db.Integer,
                          db.ForeignKey('users.id'))
    comments = db.relationship('Comment', backref='post', lazy='dynamic')

    def __repr__(self):
        return '<Post %s>' % self.title

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul', 'h1',
                        'h2', 'h3', 'p', 'hr', 'br', 'img']
        attrs = {
            '*': ['class'],
            'a': ['href', 'rel'],
            'img': ['src', 'alt'],
        }
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, attributes=attrs, strip=True))

    # 利用 forgery_py 生成虚拟数据
    @staticmethod
    def generate_fake(count=100):
        from random import seed, randint
        import forgery_py

        seed()
        user_count = User.query.count()
        for i in range(count):
            user = User.query.offset(randint(0, user_count - 1)).first()
            post = Post(body=forgery_py.lorem_ipsum.sentences(randint(1, 3)),
                        create_timestamp=forgery_py.date.date(True),
                        author=user)
            db.session.add(post)
            db.session.commit()

    def get_tags(self):
        tags_list = [tag for tag in self.tags.split(',') if tag]
        return tags_list

    @staticmethod
    def get_tags_string():
        posts = Post.query.all()
        tags_set = set()
        for post in posts:
            tags_set.update(set(post.get_tags()))
        tags_string = ' '.join(tags_set)
        return tags_string

    def get_category_name(self):
        return Category.query.get(self.category_id).name

    def to_json(self):
        post_json = {
            'url': url_for('api.get_post', id=self.id, _external=True),
            'title': self.title,
            'category': url_for('api.get_category', id=self.category_id,
                                _external=True),
            'tags': self.get_tags(),
            'body': self.body,
            'body_html': self.body_html,
            'create_time': self.create_timestamp,
            'update_time': self.update_timestamp,
            'author': url_for('api.get_user', id=self.author_id, _external=True),
            'comments': url_for('api.get_post_comments', id=self.id,
                               _external=True),
            'comment_count': self.comments.count(),
        }
        return post_json

    @staticmethod
    def from_json(post_json):
        title = post_json.get('title')
        if not title:
            raise ValueError('post does not have a title')
        category = post_json.get('category')
        if not category:
            raise ValueError('post does not have a category')
        if not Category.query.filter_by(name=category).first():
            raise ValueError('wrong category')
        tags = post_json.get('tags')
        if not tags:
            raise ValueError('post does not have tags')
        body = post_json.get('body')
        if not body:
            raise ValueError('post does not have a body')
        return Post(title=title, tags=tags, body=body)


# 当 Post 实例的 body 字段更新，on_changed_body 会被自动调用
db.event.listen(Post.body, 'set', Post.on_changed_body)


class Comment(db.Model):
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(200))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    disabled = db.Column(db.Boolean, default=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))

    def to_json(self):
        comment_json = {
            'url': url_for('api.get_comment', id=self.id, _external=True),
            'body': self.body,
            'timestamp': self.timestamp,
            'author': url_for('api.get_user', id=self.author_id, _external=True),
            'post': url_for('api.get_post', id=self.post_id, _external=True),
        }
        return comment_json

    @staticmethod
    def from_json(comment_json):
        body = comment_json.get('body')
        if not body:
            raise ValueError('comment does not have a body')
        return Comment(body=body)
