# -*- coding: utf-8 -*-


from flask_wtf import FlaskForm
from flask_babel import lazy_gettext
from wtforms import StringField, SubmitField, BooleanField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, Regexp
from wtforms import ValidationError
from flask_pagedown.fields import PageDownField
from ..models import User, Role


class EditProfileForm(FlaskForm):
    real_name = StringField(lazy_gettext('Real name'), validators=[Length(0, 64)])
    location = StringField(lazy_gettext('Location'), validators=[Length(0, 64)])
    about_me = StringField(lazy_gettext('About me'))
    submit = SubmitField(lazy_gettext('Submit'))


class EditProfileAdminForm(FlaskForm):
    email = StringField(lazy_gettext('Email'),
                        validators=[DataRequired(), Length(1, 64), Email()])
    username = StringField(lazy_gettext('Username'), validators=[
        DataRequired(), Length(1, 64), Regexp('^[A-Za-z0-9_.]*$', 0, lazy_gettext(
            'Username must have only letters, numbers, dots or underscores'))])
    confirmed = BooleanField(lazy_gettext('Confirmed'))
    role = SelectField(lazy_gettext('Role'), coerce=int)
    real_name = StringField(lazy_gettext('Real name'), validators=[Length(0, 64)])
    location = StringField(lazy_gettext('Location'), validators=[Length(0, 64)])
    about_me = TextAreaField(lazy_gettext('About me'))
    submit = SubmitField(lazy_gettext('Submit'))

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name)
                             for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
        if field.data != self.user.email and \
                User.query.filter_by(email=field.data).first():
            raise ValidationError(lazy_gettext('Email already registered'))

    def validate_username(self, field):
        if field.data != self.user.username and \
                User.query.filter_by(username=field.data).first():
            raise ValidationError(lazy_gettext('Username already in use'))


class PostForm(FlaskForm):
    body = PageDownField(lazy_gettext('Publish Post'), validators=[DataRequired()])
    submit = SubmitField(lazy_gettext('Submit'))


class CommentForm(FlaskForm):
    body = StringField('', validators=[DataRequired()])
    submit = SubmitField(lazy_gettext('Submit'))
