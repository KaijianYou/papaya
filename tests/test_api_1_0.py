# -*- coding: utf-8 -*-


import unittest

from app import create_app
from app import db
from models.category import Category
from models.role import Role
from models.user import User


class APITestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app('test')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client

        db.create_all()
        Role.insert_roles()
        Category.insert_categories()

        # 添加新用户
        r = Role.query.filter_by(name='User').first()
        self.assertIsNotNone(r)
        u = User(email='maria@fly.com', password='hello', confirmed=True, role=r)
        db.session.add(u)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
