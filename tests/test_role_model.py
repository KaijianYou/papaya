# -*- coding: utf-8 -*-


import unittest

from app import create_app
from app import db
from models.role import Role, Permission
from models.user import User


class RoleModelTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app('test')
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
