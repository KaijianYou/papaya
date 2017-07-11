# -*- coding: utf-8 -*-


from flask_mail import Message
from flask import current_app
from flask import render_template
from flask_babel import gettext as _

from app import mail
from app.decorators import async_task


class EmailUtils(object):
    @classmethod
    @async_task
    def _send_async_email(cls, app, message):
        with app.app_context():
            mail.send(message)

    @classmethod
    def _send_email(cls, subject, body, html, from_email, to_emails, cc_emails=None, bcc_emails=None):
        message = Message(subject=subject, sender=from_email, recipients=to_emails)
        message.body = body
        message.html = html
        if cc_emails:
            message.cc = cc_emails
        if bcc_emails:
            message.bcc = bcc_emails
        app = current_app._get_current_object()
        cls._send_async_email(app, message)

    @classmethod
    def _send_system_email(cls, subject, body, html, to_emails, cc_emails=None, bcc_emails=None):
        app = current_app._get_current_object()
        from_email = app.config['MAIL_SENDER']
        subject = app.config['MAIL_SUBJECT_PREFIX'] + ' ' + subject
        cls._send_email(subject, body, html, from_email, to_emails, cc_emails, bcc_emails)

    @classmethod
    def send_change_email_email(cls, **kwargs):
        to_emails = [kwargs['user'].email]
        subject = _('Confirm your email address')
        body = render_template('/auth/email/change_email.txt', **kwargs)
        html = render_template('/auth/email/change_email.html', **kwargs)
        cls._send_system_email(subject, body, html, to_emails)

    @classmethod
    def send_confirm_email(cls, **kwargs):
        to_emails = [kwargs['user'].email]
        subject = _('Confirm Your Account')
        body = render_template('auth/email/confirm.txt', **kwargs)
        html = render_template('auth/email/confirm.html', **kwargs)
        cls._send_system_email(subject, body, html, to_emails)

    @classmethod
    def send_new_user_email(cls, **kwargs):
        to_emails = [current_app.config['ADMIN_EMAIL']]
        subject = _('New user')
        body = render_template('auth/email/new_user.txt', **kwargs)
        html = render_template('auth/email/new_user.html', **kwargs)
        cls._send_system_email(subject, body, html, to_emails)

    @classmethod
    def send_reset_password_email(cls, to_emails, **kwargs):
        subject = _('Reset your password')
        body = render_template('auth/email/reset_password.txt', **kwargs)
        html = render_template('auth/email/reset_password.html', **kwargs)
        cls._send_system_email(subject, body, html, to_emails)
