# -*- coding: utf-8 -*-


"""
@Description: 
@Version: 
@Software: PyCharm
@Author: youkaijian
@Date: 2017/02/24
"""


import unittest
import time
from app.models import User
from app import db
from app import create_app


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
        u = User(username='Birdman', password='tiger', email='birdman@gmail.com')
        self.assertTrue(u.password_hash is not None)

    def test_no_password_getter(self):
        u = User(username='Birdman', password='tiger', email='birdman@gmail.com')
        with self.assertRaises(AttributeError):
            u.password

    def test_password_verification(self):
        u = User(username='Birdman', password='tiger', email='birdman@gmail.com')
        self.assertTrue(u.verify_password('tiger'))
        self.assertFalse(u.verify_password('dog'))

    def test_password_salts_are_random(self):
        u = User(username='Birdman', password='tiger', email='birdman@gmail.com')
        u2 = User(username='Birdman', password='tiger', email='birdman@gmail.com')
        self.assertTrue(u.password_hash != u2.password_hash)

    def test_valid_confirmation_token(self):
        u = User(username='Birdman', password='tiger', email='birdman@gmail.com')
        db.session.add(u)
        db.session.commit()
        token = u.generate_confirmation_token()
        self.assertTrue(u.confirm(token))

    def test_invalid_confirmation_token(self):
        u1 = User(username='Birdman', password='tiger', email='birdman@gmail.com')
        u2 = User(username='Batman', password='tiger', email='batman@gmail.com')
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
        u = User(username='Birdman', password='tiger', email='birdman@gmail.com')
        db.session.add(u)
        db.session.commit()
        time.sleep(2)
        last_visited_before = u.last_visited
        u.update_last_visited()
        self.assertTrue(u.last_visited > last_visited_before)
