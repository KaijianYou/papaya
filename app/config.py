# -*- coding: utf-8 -*-


import os


class Config(object):

    # 邮件设置
    MAIL_SUBJECT_PREFIX = 'Papaya - '
    MAIL_SENDER = 'Papaya <' + os.environ.get('MAIL_USERNAME') + '>'
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

    # 聚合数据 API 接口设置
    JUHE_WEATHER_URL = 'http://v.juhe.cn/weather/index'
    JUHE_API_KEY = '44a2fea2e2780f71257feb28b22c6048'
    JUHE_DATA_TYPE = 'json'
    JUHE_DATA_FORMAT = '1'

    # 七牛云 API 接口设置
    QINIU_ACCESS_KEY = 'EDWKdOVPLAyBiE8QK-zRg-C_AaVkriaUQmxy8BuT'
    QINIU_SECRET_KEY = 'B2sX9RcKXz6TtFYWf-3Qwb6T6CfSVYLJkSkzMKdI'

    JSON_AS_ASCII = False

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):

    NAME = 'dev'
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL')

    # Sentry 配置
    SENTRY_DSN = 'https://269ded54b4d84ca2b27c70e972653dd9:9126d7016fe941a98b4ea8ccc8d1510b@sentry.io/194714'

    # 七牛云 API 接口设置
    QINIU_BUCKET_NAME = 'papaya-dev'
    QINIU_BUCKET_DOMAIN = ''


class TestingConfig(Config):

    NAME = 'test'
    TESTING = True
    WTF_CSRF_ENABLED = False  # 禁用表单 CSRF 保护
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL')


class ProductionConfig(Config):

    NAME = 'prod'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')

    # Sentry 配置
    SENTRY_DSN = 'https://ccc720773a1040acaf1d484f9763f7db:e84abd18e1924143a554c5874305c435@sentry.io/194712'

    # 七牛云 API 接口设置
    QINIU_BUCKET_NAME = 'papaya-prod'
    QINIU_BUCKET_DOMAIN = ''

    @classmethod
    def init_app(cls, app):
        super().init_app(app)

        # 配置日志：当发生严重错误时发送电子邮件给管理员
        import logging
        from logging.handlers import SMTPHandler
        from logging.handlers import RotatingFileHandler
        from logging import Formatter

        credentials = None
        secure = None
        if getattr(cls, 'ADMIN_EMAIL', None) is not None:
            credentials = (cls.MAIL_USERNAME, cls.MAIL_PASSWORD)
            if getattr(cls, 'MAIL_USE_SSL', None):
                secure = ()

        mail_handler = SMTPHandler(
            mailhost=(cls.MAIL_SERVER, cls.MAIL_PORT),
            fromaddr=cls.MAIL_SENDER,
            toaddrs=[cls.ADMIN_EMAIL],
            subject=cls.MAIL_SUBJECT_PREFIX + 'Application Error',
            credentials=credentials,
            secure=secure)
        mail_handler.setLevel(logging.ERROR)
        mail_handler.setFormatter(Formatter('''
        Message type: %(levelname)s
        Location:     %(pathname)s:%(lineno)d
        Module:       %(module)s
        Function:     %(funcName)s
        Time:         %(asctime)s
        
        Message:
            %(message)s
        '''))
        app.logger.addHandler(mail_handler)

        file_handler = RotatingFileHandler('papaya-server.log',
                                           maxBytes=10 * 1024 * 1024,
                                           backupCount=10)
        file_handler.setLevel(logging.WARNING)
        file_handler.setFormatter(Formatter(
            '%(asctime)s %(levelname)s: %(message)s '
            '[in %(pathname)s:%(lineno)d]'
        ))
        app.logger.addHandler(file_handler)


class HerokuConfig(ProductionConfig):
    """Heroku configuration"""

    NAME = 'heroku'
    SSL_DISABLE = bool(os.environ.get('SSL_DISABLE'))

    @classmethod
    def init_app(cls, app):
        ProductionConfig.init_app(app)

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
    'default': DevelopmentConfig,
    'dev': DevelopmentConfig,
    'test': TestingConfig,
    'prod': ProductionConfig,
    'heroku': HerokuConfig,
}
