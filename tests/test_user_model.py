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
        self.app = create_app('test')
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

    def test_get_avatar_url(self):
        u = User(username='birdman', password='tiger', email='birdman@gmail.com')
        with self.app.test_request_context('/'):
            avatar_url = u.get_avatar_url()
            avatar_256_url = u.get_avatar_url(size=256)
            avatar_pg_url = u.get_avatar_url(rating='pg')
            avatar_retro_url = u.get_avatar_url(default='retro')

        with self.app.test_request_context('/', base_url='https://example.com'):
            avatar_ssl_url = u.get_avatar_url()

        self.assertTrue('http://www.gravatar.com/avatar/' +
                        '1d0a5d31e8cfa492465874300982b8c8' in avatar_url)
        self.assertTrue('s=256' in avatar_256_url)
        self.assertTrue('r=pg' in avatar_pg_url)
        self.assertTrue('d=retro' in avatar_retro_url)
        self.assertTrue('http://secure.gravatar.com/avatar/' +
                        '1d0a5d31e8cfa492465874300982b8c8' in avatar_ssl_url)

    def test_timestamps(self):
        u = User(username='birdman', password='tiger', email='birdman@gmail.com')
        db.session.add(u)
        db.session.commit()
        self.assertTrue((datetime.utcnow() - u.create_datetime).total_seconds() < 3)
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

        before_datetime = datetime.utcnow()
        u1.follow(u2)
        db.session.add(u1)
        db.session.commit()
        after_datetime = datetime.utcnow()

        self.assertTrue(u1.is_following(u2))
        self.assertFalse(u1.is_followed_by(u2))
        self.assertTrue(u2.is_followed_by(u1))
        u1_followed_count = Follow.query.filter_by(follower_id=u1.id,
                                                   enable=True).count()
        self.assertEqual(u1_followed_count, 1)
        u2_follower_count = Follow.query.filter_by(followed_id=u2.id,
                                                   enable=True).count()
        self.assertEqual(u2_follower_count, 1)

        f = Follow.query.filter_by(follower_id=u1.id).all()[-1]
        self.assertTrue(f.followed_id == u2.id)
        self.assertTrue(before_datetime <= f.create_datetime <= after_datetime)
        f = Follow.query.filter_by(followed_id=u2.id).all()[0]
        self.assertTrue(f.follower_id == u1.id)

        u1.unfollow(u2)
        db.session.add(u1)
        db.session.commit()

        u1_followed_count = Follow.query.filter_by(follower_id=u1.id,
                                                   enable=True).count()
        self.assertEqual(u1_followed_count, 0)
        u2_follower_count = Follow.query.filter_by(followed_id=u2.id,
                                                   enable=True).count()
        self.assertEqual(u2_follower_count, 0)
        self.assertEqual(Follow.query.filter_by(enable=True).count(), 0)
