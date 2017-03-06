# -*- coding: utf-8 -*-


import os


class Config(object):
    MAIL_SUBJECT_PREFIX = 'FlaskFB - '
    MAIL_SENDER = 'FlaskFB <' + os.environ.get('MAIL_USERNAME') + '>'
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL')
    MAIL_SERVER = 'smtp.qq.com'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

    POSTS_PER_PAGE = 20
    FOLLOWERS_PER_PAGE = 20
    COMMENTS_PER_PAGE = 30

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

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)

        import logging
        from logging.handlers import SMTPHandler
        credentials = None
        secure = None
        if getattr(cls, 'MAIL_USERNAME', None) is not None:
            credentials = (cls.MAIL_USERNAME, cls.MAIL_PASSWORD)
            if getattr(cls, 'MAIL_USE_SSL', None):
                secure = ()

        mail_handler = SMTPHandler(
            mailhost=(cls.MAIL_SERVER, cls.MAIL_PORT),
            fromaddr=cls.MAIL_SENDER,
            toaddrs=[cls.ADMIN_EMAIL],
            subject=cls.MAIL_SUBJECT_PREFIX + ' Application Error',
            credentials=credentials,
            secure=secure)
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)


config = {
    'default': DevelopmentConfig,
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig
}
