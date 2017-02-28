# -*- coding: utf-8 -*-


"""
@Description: 
@Version: 
@Software: PyCharm
@Author: youkaijian
@Date: 2017/02/23
"""


import os


class Config:
    DEBUG = True
    MAIL_SUBJECT_PREFIX = 'FlaskFB - '
    MAIL_SENDER = 'FlaskFB <kaijianyou@foxmail.com>'
    FLASKFB_ADMIN = os.environ.get('FLASKFB_ADMIN')
    MAIL_SERVER = 'smtp.qq.com'
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'

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
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL')


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')


config = {
    'default': DevelopmentConfig,
    # 'default': TestingConfig,
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig
}
