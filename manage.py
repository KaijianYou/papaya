#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import os

from flask_script import Manager
from flask_script import Shell
from flask_migrate import Migrate, MigrateCommand

from app import create_app
from app import db
from app.models import User, Role, Post, Permission, Comment, Category


COV = None
if os.environ.get('FLASK_COVERAGE'):
    import coverage
    COV = coverage.coverage(branch=True, include='app/*')
    COV.start()


app = create_app(os.getenv('FLASKFB_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)


def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role, Permission=Permission,
                Post=Post, Comment=Comment, Category=Category)


manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


@manager.command
def deploy():
    """部署"""
    from flask_migrate import upgrade
    from app.models import Role, User

    # 迁移数据库到最新版本
    upgrade()

    Role.insert_roles()
    User.add_self_follows()
    Category.insert_categories()


@manager.command
def test(coverage=False):
    """运行单元测试"""
    if coverage and not os.environ.get('FLASK_COVERAGE'):
        import sys
        os.environ['FLASK_COVERAGE'] = '1'
        os.execvp(sys.executable, [sys.executable] + sys.argv)

    import unittest
    tests = unittest.TestLoader().discover(start_dir='tests')
    unittest.TextTestRunner(verbosity=2).run(tests)

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


# 源码分析器
@manager.command
def profile(length=20, profile_dir=None):
    """启动应用的同时开启源码分析器"""
    from werkzeug.contrib.profiler import ProfilerMiddleware
    app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[length],
                                     profile_dir=profile_dir)
    app.run()


if __name__ == '__main__':
    manager.run()
