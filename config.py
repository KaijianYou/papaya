# -*- coding: utf-8 -*-


import os


class Config(object):
    MAIL_SUBJECT_PREFIX = 'FlaskFB - '
    MAIL_SENDER = 'FlaskFB <' + os.environ.get('MAIL_USERNAME') + '>'
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL')
    MAIL_SERVER = 'smtp.qq.com'
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

    POSTS_PER_PAGE = 10
    FOLLOWERS_PER_PAGE = 10
    COMMENTS_PER_PAGE = 10

    SECRET_KEY = os.environ.get('SECRET_KEY') or 'no zuo no die why you try'

    BABEL_DEFAULT_LOCALE = 'zh_Hans_CN'
    # BABEL_DEFAULT_TIMEZONE =

    SQLALCHEMY_RECORD_QUERIES = True  # 启用数据库查询性能记录功能
    DB_QUERY_TIMEOUT = 0.5            # 花费时间超过 0.5s 的查询语句将被记录
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # SQLALCHEMY_COMMIT_ON_TEARDOWN = True  # Flask-SQLALchemy 未来可能会删除

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL')


class TestingConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False  # 禁用表单 CSRF 保护
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL')


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')


config = {
    'default': DevelopmentConfig,
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig
}
