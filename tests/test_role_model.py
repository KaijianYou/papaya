# -*- coding: utf-8 -*-


"""
@Description: 
@Version: 
@Software: PyCharm
@Author: youkaijian
@Date: 2017/02/26
"""


import unittest
from app.models import Role, User, AnonymousUser, Permission
from app import db
from app import create_app


class RoleModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_roles_and_permissions(self):
        Role.insert_roles()
        u = User(email='keff@exp.com', password='tiger')
        self.assertTrue(u.can(Permission.WRITE_ARTICLES))
        self.assertFalse(u.can(Permission.MODERATE_COMMENTS))

    def test_anonymous_user_permission(self):
        u = AnonymousUser()
        self.assertFalse(u.can(Permission.FOLLOW))
