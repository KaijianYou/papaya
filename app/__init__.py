# -*- coding: utf-8 -*-


from flask import Flask
from flask_babel import Babel
from flask_babel import lazy_gettext as lazy_
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_mail import Mail
from flask_moment import Moment
from flask_pagedown import PageDown
from flask_sqlalchemy import SQLAlchemy
from raven.contrib.flask import Sentry

from config import config


bootstrap = Bootstrap()
moment = Moment()
db = SQLAlchemy()
mail = Mail()
pagedown = PageDown()
babel = Babel()
sentry = Sentry()
login_manager = LoginManager()


def register_extensions(app):
    bootstrap.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    mail.init_app(app)
    pagedown.init_app(app)
    babel.init_app(app)

    env = app.config['NAME']
    if env == 'Development' or env == 'Production':
        sentry.init_app(app, dsn=app.config['SENTRY_DSN'])

    from models.user import User, AnonymousUser

    login_manager.init_app(app)
    login_manager.session_protection = 'basic'
    login_manager.login_view = 'auth.login'
    login_manager.refresh_view = 'auth.login'
    login_manager.login_message = lazy_('Please log in to access this page')
    login_manager.anonymous_user = AnonymousUser

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))


def register_blueprint(app):
    from app.main import main as main_blueprint
    from app.main import views, errors
    app.register_blueprint(main_blueprint)

    from app.auth import auth as auth_blueprint
    from app.auth import views
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from app.admin import admin as admin_blueprint
    from app.admin import views
    from app.admin.auth import views
    from app.admin.user import views
    from app.admin.comment import views
    from app.admin.article import views
    app.register_blueprint(admin_blueprint, url_prefix='/admin')

    from .api_1_0 import api as api_1_0_blueprint
    from .api_1_0 import authentication, articles, users, comments, categories, errors
    app.register_blueprint(api_1_0_blueprint, url_prefix='/api/v1.0')


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    register_extensions(app)

    if not app.debug and not app.testing and not app.config['SSL_DISABLE']:
        from flask_sslify import SSLify
        sslify = SSLify(app)

    register_blueprint(app)

    return app
