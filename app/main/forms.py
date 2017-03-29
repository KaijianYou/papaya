# -*- coding: utf-8 -*-


from flask_wtf import FlaskForm
from flask_babel import lazy_gettext as lazy_
from wtforms import StringField, SubmitField, BooleanField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, Regexp
from wtforms import ValidationError
from flask_pagedown.fields import PageDownField

from ..models import User, Role


class EditProfileForm(FlaskForm):
    real_name = StringField(lazy_('Real name'),
                            validators=[Length(0, 64)],
                            render_kw={'placeholder': lazy_('Real name')})
    location = StringField(lazy_('Location'),
                           validators=[Length(0, 64)],
                           render_kw={'placeholder': lazy_('Location')})
    about_me = StringField(lazy_('About me'),
                           render_kw={'placeholder': lazy_('About me')})
    submit = SubmitField(lazy_('Submit'))


class EditProfileAdminForm(FlaskForm):
    email = StringField(lazy_('Email'),
                        validators=[DataRequired(), Length(1, 64), Email()],
                        render_kw={'placeholder': lazy_('Email')})
    username = StringField(lazy_('Username'),
                           validators=[DataRequired(), Length(1, 64),
                                       Regexp('^[A-Za-z0-9_.]*$', 0,
                                              lazy_('Username must have only'
                                                    ' letters, numbers, dots'
                                                    ' or underscores'))],
                           render_kw={'placeholder': lazy_('Username')})
    confirmed = BooleanField(lazy_('Confirmed'))
    role = SelectField(lazy_('Role'), coerce=int,
                       render_kw={'placeholder': lazy_('Role')})
    real_name = StringField(lazy_('Real name'), validators=[Length(0, 64)],
                            render_kw={'placeholder': lazy_('Real name')})
    location = StringField(lazy_('Location'), validators=[Length(0, 64)],
                           render_kw={'placeholder': lazy_('Location')})
    about_me = TextAreaField(lazy_('About me'),
                             render_kw={'placeholder': lazy_('About me')})
    submit = SubmitField(lazy_('Submit'))

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name)
                             for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
        if field.data != self.user.email and \
                User.query.filter_by(email=field.data).first():
            raise ValidationError(lazy_('Email already registered'))

    def validate_username(self, field):
        if field.data != self.user.username and \
                User.query.filter_by(username=field.data).first():
            raise ValidationError(lazy_('Username already in use'))


class PostForm(FlaskForm):
    title = StringField(lazy_('Title'),
                        validators=[DataRequired(), Length(1, 64)],
                        render_kw={'placeholder': lazy_('Title')})
    category = StringField(lazy_('Category'),
                           validators=[DataRequired(), Length(1, 64)],
                           render_kw={'placeholder': lazy_('Category')})
    tags = StringField(lazy_('Tag'),
                       validators=[DataRequired(), Length(1, 200)],
                       render_kw={'placeholder': lazy_('Tag')})
    body = PageDownField(lazy_('Post'), validators=[DataRequired()])
    submit = SubmitField(lazy_('Publish'))


class CommentForm(FlaskForm):
    body = TextAreaField('',
                         validators=[DataRequired(), Length(1, 200)],
                         render_kw={'placeholder':
                                    lazy_('Limited to 200 characters')})
    submit = SubmitField(lazy_('Submit'))
