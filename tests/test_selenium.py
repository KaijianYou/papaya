import unittest
import threading

from selenium import webdriver

from app import create_app, db
from models.role import Role
from models.user import User
from models.category import Category
from utils.fake_util import FakeUtil


class SeleniumTestCase(unittest.TestCase):
    client = None

    @classmethod
    def setUpClass(cls):
        try:
            cls.client = webdriver.Chrome('./chromedriver')
        except Exception:
            pass

        if not cls.client:
            return

        cls.app = create_app('test')
        cls.app_context = cls.app.app_context()
        cls.app_context.push()

        # 禁止日志
        import logging
        logger = logging.getLogger('werkzeug')
        logger.setLevel('ERROR')

        db.create_all()
        Role.insert_roles()
        Category.insert_categories()
        FakeUtil.generate_fake_users(10)
        FakeUtil.generate_fake_articles(10)

        admin_role = Role.query.filter_by(name='Administrator').first()
        admin = User(email='singledog@gmail.com', username='john',
                     password='dog', role=admin_role, confirmed=True)
        db.session.add(admin)
        db.session.commit()

        threading.Thread(target=cls.app.run).start()

    @classmethod
    def tearDownClass(cls):
        if not cls.client:
            return

        # 关闭 Flask 服务器和浏览器
        cls.client.get('http://localhost:5000/shutdown')
        cls.client.close()

        db.drop_all()
        db.session.remove()

        cls.app_context.pop()

    def setUp(self):
        if not self.client:
            self.skipTest('Web browser not available')

    def tearDown(self):
        pass

    def test_admin_home_page(self):
        import re
        self.client.get('http://localhost:5000/')
        self.assertTrue(re.search('Stranger', self.client.page_source))

        self.client.find_element_by_link_text('Log In').click()
        self.assertTrue('Log In' in self.client.page_source)

        self.client.find_element_by_name('email').send_keys('singledog@gmail.com')
        self.client.find_element_by_name('password').send_keys('dog')
        self.client.find_element_by_name('submit').click()
        self.assertTrue(re.search('john', self.client.page_source))
