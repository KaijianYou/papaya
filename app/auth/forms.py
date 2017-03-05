# -*- coding: utf-8 -*-


from flask_wtf import FlaskForm
from flask_babel import lazy_gettext
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from ..models import User


class LoginForm(FlaskForm):
    email = StringField(lazy_gettext('Email'),
                        validators=[DataRequired(), Length(1, 64), Email()])
    password = PasswordField(lazy_gettext('Password'), validators=[DataRequired()])
    remeber_me = BooleanField(lazy_gettext('Keep me logged in'))
    submit = SubmitField(lazy_gettext('Log In'))


class RegistrationForm(FlaskForm):
    email = StringField(lazy_gettext('Email'),
                        validators=[DataRequired(), Length(1, 64), Email()])
    username = StringField(lazy_gettext('Username'), validators=[
        DataRequired(), Length(1, 64), Regexp('^[A-Za-z0-9_.]*$', 0, lazy_gettext(
            'Username must have only letters, numbers, dots or underscores'))])
    password = PasswordField(lazy_gettext('Password'), validators=[DataRequired()])
    duplicate_password = PasswordField(lazy_gettext('Confirm password'), validators=[
        DataRequired(), EqualTo('password', message=lazy_gettext('Passwords must match'))])
    submit = SubmitField(lazy_gettext('Register'))

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError(lazy_gettext('Email already registered'))

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError(lazy_gettext('Username already in use'))


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField(
        lazy_gettext('Old password'), validators=[DataRequired()])
    new_password = PasswordField(
        lazy_gettext('New password'), validators=[DataRequired()])
    duplicate_new_password = PasswordField(
        lazy_gettext('Confirm new password'),
        validators=[
            DataRequired(), EqualTo('new_password', message=lazy_gettext('Passwords must match'))
        ])
    submit = SubmitField(lazy_gettext('Update Password'))


class ResetPasswordRequestForm(FlaskForm):
    email = StringField(lazy_gettext('Email'),
                        validators=[DataRequired(), Length(1, 64), Email()])
    submit = SubmitField(lazy_gettext('Reset Password'))

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first() is None:
            raise ValidationError(lazy_gettext('Unknown email address'))


class ResetPasswordForm(FlaskForm):
    email = StringField(lazy_gettext('Email'),
                        validators=[DataRequired(), Length(1, 64), Email()])
    password = PasswordField(lazy_gettext('New password'), validators=[DataRequired()])
    duplicate_password = PasswordField(lazy_gettext('Confirm new password'), validators=[
        DataRequired(), EqualTo('password', message=lazy_gettext('Passwords must match'))])
    submit = SubmitField(lazy_gettext('Reset Password'))

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first() is None:
            raise ValidationError(lazy_gettext('Unknown email address'))


class ChangeEmailForm(FlaskForm):
    email = StringField(lazy_gettext('New email'),
                        validators=[DataRequired(), Length(1, 64), Email()])
    password = PasswordField(lazy_gettext('Password'), validators=[DataRequired()])
    submit = SubmitField(lazy_gettext('Update Email Address'))

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError(lazy_gettext('Email already registered'))
