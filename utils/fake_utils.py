# -*- coding: utf-8 -*-


from app import db
from models.user import User
from models.post import Post


class FakeUtils(object):
    """利用 forgery_py 生成虚拟数据"""

    @staticmethod
    def generate_fake_users(count=100):
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

    @staticmethod
    def generate_fake_posts(count=100):
        from random import seed, randint
        import forgery_py

        seed()
        user_count = User.query.count()
        for i in range(count):
            user = User.query.offset(randint(0, user_count - 1)).first()
            post = Post(body=forgery_py.lorem_ipsum.sentences(randint(1, 3)),
                        create_datetime=forgery_py.date.date(True),
                        author=user)
            db.session.add(post)
            db.session.commit()
