# -*- coding: utf-8 -*-


from random import seed, randint

import forgery_py
from sqlalchemy.exc import IntegrityError

from app import db
from models.user import User
from models.article import Article
from models.category import Category


class FakeUtils(object):
    """利用 forgery_py 生成虚拟数据"""

    @staticmethod
    def generate_fake_users(count=100):
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

    @staticmethod
    def generate_fake_articles(count=100):
        seed()
        user_count = User.query.count()
        category_count = Category.query.count()
        for i in range(count):
            user = User.query.offset(randint(0, user_count - 1)).first()
            category = Category.query.offset(randint(0, category_count - 1)).first()
            article = Article(body=forgery_py.lorem_ipsum.sentences(randint(1, 3)),
                              tags='', category=category, author=user)
            db.session.add(article)
            db.session.commit()
