# -*- coding: utf-8 -*-


import unittest
import re

from flask import url_for

from app import create_app, db
from app.models import User, Role, Category


class FlaskClientTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client(use_cookies=True)

        db.create_all()
        Role.insert_roles()
        Category.insert_categories()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_home_page(self):
        response = self.client.get(url_for('main.index'))
        # self.assertTrue('Stranger' in response.get_data(as_text=True))
        self.assertTrue('游客' in response.get_data(as_text=True))

    def test_register_and_login(self):
        response = self.client.post(url_for('auth.register'), data={
            'email': 'sugar@gmail.com',
            'username': 'sugar',
            'password': 'tiger',
            'password_confirmation': 'tiger'
        })
        self.assertTrue(response.status_code == 302)

        response = self.client.post(url_for('auth.login'), data={
            'email': 'sugar@gmail.com',
            'password': 'tiger'
        }, follow_redirects=True)
        data = response.get_data(as_text=True)
        # self.assertTrue(re.search('Hello,\s+sugar!', data))
        self.assertTrue(re.search('您好,\s+sugar', data))
        # self.assertTrue('You have not confirmed your account yet' in data)
        self.assertTrue('您还没有验证账号' in data)

        user = User.query.filter_by(email='sugar@gmail.com').first()
        token = user.generate_confirmation_token()
        response = self.client.get(url_for('auth.confirm', token=token),
                                   follow_redirects=True)
        data = response.get_data(as_text=True)
        # self.assertTrue('You have confirmed your account' in data)
        self.assertTrue('您已经验证账号' in data)

        response = self.client.get(url_for('auth.logout'), follow_redirects=True)
        data = response.get_data(as_text=True)
        # self.assertTrue('You have been logged out' in data)
        self.assertTrue('您已经退出' in data)
