# -*- coding: utf-8 -*-


from flask_babel import lazy_gettext as lazy_
from flask_pagedown.fields import PageDownField
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, SelectField, \
    TextAreaField
from wtforms import ValidationError
from wtforms.validators import DataRequired, Length, Email, Regexp

from models.category import Category
from models.role import Role
from models.user import User


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
                           validators=[DataRequired(),
                                       Length(1, 64),
                                       Regexp('^[A-Za-z0-9_.]*$',
                                              0,
                                              lazy_('Username must have only'
                                                    ' letters, numbers, "."'
                                                    ' or "_"'))],
                           render_kw={'placeholder': lazy_('Username')})
    confirmed = BooleanField(lazy_('Confirmed'))
    role = SelectField(lazy_('Role'),
                       coerce=int,
                       render_kw={'placeholder': lazy_('Role')})
    real_name = StringField(lazy_('Real name'),
                            validators=[Length(0, 64)],
                            render_kw={'placeholder': lazy_('Real name')})
    location = StringField(lazy_('Location'),
                           validators=[Length(0, 64)],
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
    category = SelectField(lazy_('Category'),
                           coerce=int,
                           render_kw={'placeholder': lazy_('Category')})
    tags = StringField(lazy_('Tag'),
                       validators=[DataRequired(), Length(1, 200)],
                       render_kw={'placeholder': lazy_('More than one tag should'
                                                       ' separate them by comma')})
    body = PageDownField(lazy_('Post'), validators=[DataRequired()])
    submit = SubmitField(lazy_('Publish'))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.category.choices = \
            [(category.id, category.name)
             for category in Category.query.order_by(Category.name).all()]


class CommentForm(FlaskForm):

    body = TextAreaField('',
                         validators=[DataRequired(), Length(1, 200)],
                         render_kw={'placeholder': lazy_('Limited to 200 characters')})
    submit = SubmitField(lazy_('Submit'))


class WeatherForm(FlaskForm):
    city = StringField(lazy_('City'),
                       validators=[DataRequired(), Length(1, 10)],
                       render_kw={'placeholder': lazy_('City')})
    submit = SubmitField(lazy_('Search'))
