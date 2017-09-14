# -*- coding: utf-8 -*-


import hashlib
from datetime import datetime

from flask import current_app
from flask import request
from flask import url_for
from flask_login import UserMixin, AnonymousUserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from werkzeug.security import generate_password_hash, check_password_hash

from app import db
from models.base import BaseMixin
from models.article import Article
from models.follow import Follow
from models.role import Role


class User(db.Model, UserMixin, BaseMixin):
    __tablename__ = 'users'

    username = db.Column(db.String(64), nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    real_name = db.Column(db.String(64))
    email = db.Column(db.String(64), unique=True, index=True, nullable=False)
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    last_visited = db.Column(db.DateTime(), default=datetime.utcnow)
    confirmed = db.Column(db.Boolean, default=False)
    avatar_hash = db.Column(db.String(32))
    avatar_url = db.Column(db.String(256))
    role_id = db.Column('role_id', db.Integer, db.ForeignKey('roles.id'))
    articles = db.relationship('Article', backref='author', lazy='dynamic')
    comments = db.relationship('Comment', backref='author', lazy='dynamic')
    followed = db.relationship('Follow',
                               foreign_keys=[Follow.follower_id],
                               backref=db.backref('follower', lazy='joined'),
                               lazy='dynamic',
                               cascade='all, delete-orphan')
    followers = db.relationship('Follow',
                                foreign_keys=[Follow.followed_id],
                                backref=db.backref('followed', lazy='joined'),
                                lazy='dynamic',
                                cascade='all, delete-orphan')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

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

    def update_last_visited(self):
        self.last_visited = datetime.utcnow()
        db.session.add(self)
        db.session.commit()

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

    @property
    def followed_articles(self):
        """获取已关注用户的文章"""
        return Article.query\
            .join(Follow, Follow.followed_id == Article.author_id)\
            .filter(Follow.follower_id == self.id)

    def to_dict(self):
        return {
            'url': url_for('api.get_user', id=self.id, _external=True),
            'username': self.username,
            'about_me': self.about_me,
            'last_visit': self.last_visited,
            'articles': url_for('api.get_user_articles', id=self.id, _external=True),
            'followed_articles': url_for('api.get_user_followed_articles', id=self.id,
                                      _external=True),
            'article_count': self.articles.count(),
        }


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False
