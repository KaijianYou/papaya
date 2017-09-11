# -*- coding: utf-8 -*-


from flask_babel import lazy_gettext as lazy_
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms import ValidationError
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo

from models.user import User


class LoginForm(FlaskForm):

    email = StringField(lazy_('Email'),
                        validators=[DataRequired(), Length(1, 64), Email()],
                        render_kw={'placeholder': lazy_('Email')})
    password = PasswordField(lazy_('Password'),
                             validators=[DataRequired()],
                             render_kw={'placeholder': lazy_('Password')})
    remeber_me = BooleanField(lazy_('Keep me logged in'))
    submit = SubmitField(lazy_('Log In'))


class RegistrationForm(FlaskForm):

    email = StringField(lazy_('Email'),
                        validators=[DataRequired(), Length(1, 64), Email()],
                        render_kw={'placeholder': lazy_('Email')})
    username = StringField(lazy_('Username'),
                           validators=[DataRequired(),
                                       Length(1, 64),
                                       Regexp('^[A-Za-z0-9_.]+$',
                                              0,
                                              lazy_('Username must have only'
                                                    ' letters, numbers, "."'
                                                    ' or "_"'))],
                           render_kw={'placeholder': lazy_('Username')})
    password = PasswordField(lazy_('Password'),
                             validators=[DataRequired(),
                                         Regexp('^[A-Za-z0-9_.@#]+$',
                                                0,
                                                lazy_('Password must have only'
                                                      ' letters, numbers, ".",'
                                                      ' "_", "@" or "#"'))],
                             render_kw={'placeholder': lazy_('Password')})
    password_confirmation = \
        PasswordField(lazy_('Confirm password'),
                      validators=[DataRequired(),
                                  EqualTo('password',
                                          message=lazy_('Passwords must match'))],
                      render_kw={'placeholder': lazy_('Confirm password')})
    submit = SubmitField(lazy_('Register'))

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError(lazy_('Email already registered'))

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError(lazy_('Username already in use'))


class ChangePasswordForm(FlaskForm):

    old_password = PasswordField(lazy_('Old password'),
                                 validators=[DataRequired()],
                                 render_kw={'placeholder': lazy_('Old password')})
    new_password = PasswordField(lazy_('New password'),
                                 validators=[DataRequired()],
                                 render_kw={'placeholder': lazy_('New password')})
    new_password_confirmation = \
        PasswordField(lazy_('Confirm new password'),
                      validators=[DataRequired(),
                                  EqualTo('new_password',
                                          message=lazy_('Passwords must match'))],
                      render_kw={'placeholder': lazy_('Confirm new password')})
    submit = SubmitField(lazy_('Update Password'))


class ResetPasswordRequestForm(FlaskForm):

    email = StringField(lazy_('Email'),
                        validators=[DataRequired(), Length(1, 64), Email()],
                        render_kw={'placeholder': lazy_('Email')})
    submit = SubmitField(lazy_('Reset Password'))

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first() is None:
            raise ValidationError(lazy_('Unknown email address'))


class ResetPasswordForm(FlaskForm):

    email = StringField(lazy_('Email'),
                        validators=[DataRequired(), Length(1, 64), Email()])
    password = PasswordField(lazy_('New password'), validators=[DataRequired()])
    password_confirmation = \
        PasswordField(lazy_('Confirm new password'),
                      validators=[DataRequired(),
                                  EqualTo('password',
                                          message=lazy_('Passwords must match'))])
    submit = SubmitField(lazy_('Reset Password'))

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first() is None:
            raise ValidationError(lazy_('Unknown email address'))


class ChangeEmailForm(FlaskForm):

    email = StringField(lazy_('New email'),
                        validators=[DataRequired(), Length(1, 64), Email()],
                        render_kw={'placeholder': lazy_('New email')})
    password = PasswordField(lazy_('Password'),
                             validators=[DataRequired()],
                             render_kw={'placeholder': lazy_('Password')})
    submit = SubmitField(lazy_('Update Email Address'))

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError(lazy_('Email already registered'))
