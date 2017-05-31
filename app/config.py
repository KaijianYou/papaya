# -*- coding: utf-8 -*-


import os


class Config(object):
    # 邮件设置
    MAIL_SUBJECT_PREFIX = 'FlaskFB - '
    MAIL_SENDER = 'FlaskFB <' + os.environ.get('MAIL_USERNAME') + '>'
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL')
    MAIL_SERVER = 'smtp.qq.com'
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

    # 分页设置
    POSTS_PER_PAGE = 10
    FOLLOWERS_PER_PAGE = 20
    COMMENTS_PER_PAGE = 20

    SECRET_KEY = os.environ.get('SECRET_KEY') or 'WhyNotGoDie?'

    # 国际化设置
    BABEL_DEFAULT_LOCALE = 'zh_Hans_CN'
    # BABEL_DEFAULT_TIMEZONE =

    SQLALCHEMY_RECORD_QUERIES = True  # 启用数据库查询性能记录功能
    DB_QUERY_TIMEOUT = 0.5            # 花费时间超过 0.5s 的查询语句将被记录
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # SQLALCHEMY_COMMIT_ON_TEARDOWN = True  # Flask-SQLALchemy 未来可能会删除
    # SQLALCHEMY_ECHO = True  # 在 stderr 输出生成的 SQL 语句

    SSL_DISABLE = True

    # 表单设置
    WTF_CSRF_SECRET_KEY = 'NotTellYou'
    WTF_CSRF_ENABLED = True
    WTF_CSRF_CHECK_DEFAULT = True
    WTF_CSRF_TIME_LIMIT = 20 * 60

    @staticmethod
    def init_app(app):
        pass


class DevConfig(Config):
    NAME = 'dev'
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL')


class TestConfig(Config):
    NAME = 'test'
    TESTING = True
    WTF_CSRF_ENABLED = False  # 禁用表单 CSRF 保护
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL')


class ProdConfig(Config):
    NAME = 'prod'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')

    @classmethod
    def init_app(cls, app):
        super().init_app(app)

        # 配置日志：当发生严重错误时发送电子邮件给管理员
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


class HerokuConfig(ProdConfig):
    """Heroku configuration"""
    NAME = 'heroku'
    SSL_DISABLE = bool(os.environ.get('SSL_DISABLE'))

    @classmethod
    def init_app(cls, app):
        ProdConfig.init_app(app)

        # 配置日志，将日志写入 stderr，Heroku 可以捕获到输出的日志，在 Heroku
        # 客户端中通过 heroku logs 命令可以查看到这些日志
        import logging
        from logging import StreamHandler
        file_handler = StreamHandler()
        file_handler.setLevel(logging.WARNING)
        app.logger.addHandler(file_handler)

        # 使用 ProxyFix 处理代理服务器首部，任何使用反向代理的环境都要这样做
        from werkzeug.contrib.fixers import ProxyFix
        app.wsgi_app = ProxyFix(app.wsgi_app)


config = {
    'default': DevConfig,
    'dev': DevConfig,
    'test': TestConfig,
    'prod': ProdConfig,
    'heroku': HerokuConfig,
}
