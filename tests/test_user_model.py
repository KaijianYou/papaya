# -*- coding: utf-8 -*-


import time
import unittest
from datetime import datetime

from app import create_app
from app import db
from models.follow import Follow
from models.role import Permission
from models.user import User, AnonymousUser


class UserModelTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_setter(self):
        u = User(username='birdman', password='tiger', email='birdman@gmail.com')
        self.assertTrue(u.password_hash is not None)

    def test_no_password_getter(self):
        u = User(username='birdman', password='tiger', email='birdman@gmail.com')
        with self.assertRaises(AttributeError):
            u.password

    def test_password_verification(self):
        u = User(username='birdman', password='tiger', email='birdman@gmail.com')
        self.assertTrue(u.verify_password('tiger'))
        self.assertFalse(u.verify_password('dog'))

    def test_password_salts_are_random(self):
        u = User(username='birdman', password='tiger', email='birdman@gmail.com')
        u2 = User(username='birdman', password='tiger', email='birdman@gmail.com')
        self.assertTrue(u.password_hash != u2.password_hash)

    def test_valid_confirmation_token(self):
        u = User(username='birdman', password='tiger', email='birdman@gmail.com')
        db.session.add(u)
        db.session.commit()
        token = u.generate_confirmation_token()
        self.assertTrue(u.confirm(token))

    def test_invalid_confirmation_token(self):
        u1 = User(username='birdman', password='tiger', email='birdman@gmail.com')
        u2 = User(username='batman', password='tiger', email='batman@gmail.com')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        token = u1.generate_confirmation_token()
        self.assertFalse(u2.confirm(token))

    def test_expired_confirmation_token(self):
        u = User(username='lionheart', password='tiger', email='lionheart@gmail.com')
        db.session.add(u)
        db.session.commit()
        token = u.generate_confirmation_token(1)
        time.sleep(2)
        self.assertFalse(u.confirm(token))

    def test_update_last_visited(self):
        u = User(username='birdman', password='tiger', email='birdman@gmail.com')
        db.session.add(u)
        db.session.commit()
        time.sleep(2)
        last_visited_before = u.last_visited
        u.update_last_visited()
        self.assertTrue(u.last_visited > last_visited_before)

    def test_get_avatar(self):
        u = User(username='birdman', password='tiger', email='birdman@gmail.com')
        with self.app.test_request_context('/'):
            avatar = u.get_avatar()
            avatar_256 = u.get_avatar(size=256)
            avatar_pg = u.get_avatar(rating='pg')
            avatar_retro = u.get_avatar(default='retro')

        with self.app.test_request_context('/', base_url='https://example.com'):
            avatar_ssl = u.get_avatar()

        self.assertTrue('http://www.gravatar.com/avatar/' +
                        '1d0a5d31e8cfa492465874300982b8c8' in avatar)
        self.assertTrue('s=256' in avatar_256)
        self.assertTrue('r=pg' in avatar_pg)
        self.assertTrue('d=retro' in avatar_retro)
        self.assertTrue('http://secure.gravatar.com/avatar/' +
                        '1d0a5d31e8cfa492465874300982b8c8' in avatar_ssl)

    def test_timestamps(self):
        u = User(username='birdman', password='tiger', email='birdman@gmail.com')
        db.session.add(u)
        db.session.commit()
        self.assertTrue((datetime.utcnow() - u.register_date).total_seconds() < 3)
        self.assertTrue((datetime.utcnow() - u.last_visited).total_seconds() < 3)

    def test_duplicate_email_change_token(self):
        u1 = User(username='birdman', password='tiger', email='birdman@gmail.com')
        u2 = User(username='lionheart', password='tiger', email='lionheart@gmail.com')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        token = u2.generate_email_change_token('birdman@gmail.com')
        self.assertFalse(u2.change_email(token))
        self.assertTrue(u2.email == 'lionheart@gmail.com')

    def test_anonymous_user_permission(self):
        u = AnonymousUser()
        self.assertFalse(u.can(Permission.FOLLOW))

    def test_follows(self):
        u1 = User(username='birdman', email='birdman@gmail.com', password='tiger')
        u2 = User(username='lionheart', email='batman@gmail.com', password='lion')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        self.assertFalse(u1.is_following(u2))
        self.assertFalse(u1.is_followed_by(u2))

        timestamp_before = datetime.utcnow()
        u1.follow(u2)
        db.session.add(u1)
        db.session.commit()
        timestamp_after = datetime.utcnow()
        self.assertTrue(u1.is_following(u2))
        self.assertFalse(u1.is_followed_by(u2))
        self.assertTrue(u2.is_followed_by(u1))
        self.assertTrue(u1.followed.count() == 2)
        self.assertTrue(u2.followers.count() == 2)

        f = u1.followed.all()[-1]
        self.assertTrue(f.followed == u2)
        self.assertTrue(timestamp_before <= f.timestamp <= timestamp_after)
        f = u2.followers.all()[0]
        self.assertTrue(f.follower == u1)

        u1.unfollow(u2)
        db.session.add(u1)
        db.session.commit()
        self.assertTrue(u1.followed.count() == 1)
        self.assertTrue(u2.followers.count() == 1)
        self.assertTrue(Follow.query.count() == 2)

        u2.follow(u1)
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        db.session.delete(u2)
        db.session.commit()
        self.assertTrue(Follow.query.count() == 1)
