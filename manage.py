#!/usr/bin/env python3


import os

from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from flask_script import Shell

from app import create_app
from app import db
from models.category import Category
from models.article import Article
from models.comment import Comment
from models.role import Role, Permission
from models.user import User
from models.follow import Follow
from models.collection import Collection
from models.article_vote import ArticleVote


def make_shell_context():
    return dict(
        app=app,
        db=db,
        User=User,
        Role=Role,
        Permission=Permission,
        Article=Article,
        Comment=Comment,
        Category=Category,
        Follow=Follow,
        Collection=Collection,
        ArticleVote=ArticleVote
    )


app = create_app(os.getenv('PAPAYA_CONFIG') or 'default')

manager = Manager(app)
manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)

migrate = Migrate(app, db)


@manager.command
def deploy():
    """部署"""
    from flask_migrate import upgrade

    # 迁移数据库到最新版本
    upgrade()

    Role.insert_roles()
    Category.insert_categories()


COV = None
if os.environ.get('FLASK_COVERAGE'):
    import coverage

    COV = coverage.coverage(branch=True, include='app/*')
    COV.start()


@manager.command
def test(coverage=False):
    """测试"""
    if coverage and not os.environ.get('FLASK_COVERAGE'):
        import sys

        os.environ['FLASK_COVERAGE'] = '1'
        os.execvp(sys.executable, [sys.executable] + sys.argv)

    # 单元测试
    import unittest
    tests = unittest.TestLoader().discover(start_dir='tests')
    unittest.TextTestRunner(verbosity=2).run(tests)

    # 获取代码测试覆盖率
    if COV:
        COV.stop()
        COV.save()
        print('Coverage Summary:')
        COV.report()
        basedir = os.path.abspath(os.path.dirname(__file__))
        covdir = os.path.join(basedir, 'coverage')
        COV.html_report(directory=covdir)
        print('HTML version: file://%s/index.html' % covdir)
        COV.erase()


@manager.command
def profile(length=20, profile_dir=None):
    """源码分析器"""
    from werkzeug.contrib.profiler import ProfilerMiddleware

    # 启动应用的同时开启源码分析器
    app.wsgi_app = ProfilerMiddleware(app.wsgi_app,
                                      restrictions=[length],
                                      profile_dir=profile_dir)
    app.run()


if __name__ == '__main__':
    manager.run()
