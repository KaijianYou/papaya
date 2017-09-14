# -*- coding: utf-8 -*-


from app import db
from models.base import BaseMixin


class Permission:
    FOLLOW = 0x01  # 关注别人
    COMMENT = 0x02  # 发表评论
    WRITE_ARTICLE = 0x04  # 发布文章
    MODERATE_COMMENT = 0x08  # 管理评论
    MODERATE_ARTICLE = 0x10  # 管理文章
    MODERATE_USER = 0x20  # 管理用户
    ASSIGN_MODERATOR = 0x40  # 任命管理员


class Role(db.Model, BaseMixin):
    __tablename__ = 'roles'

    name = db.Column(db.String(64), unique=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @staticmethod
    def insert_roles():
        """
        匿名用户：未登录的用户。只有阅读文章权限
        普通用户：具有发布文章、发表评论和关注其他用户的权限。新用户的默认角色
        协管员：管理评论和文章的权限
        管理员：具有所有权限，包括修改其他用户所属角色的权限，任命协管员的权限
        """
        roles = {
            'User': (
                Permission.FOLLOW |
                Permission.COMMENT |
                Permission.WRITE_ARTICLE
            ),
            'Moderator': (
                Permission.FOLLOW |
                Permission.COMMENT |
                Permission.WRITE_ARTICLE |
                Permission.MODERATE_COMMENT |
                Permission.MODERATE_ARTICLE
            ),
            'Administrator': (
                Permission.FOLLOW |
                Permission.COMMENT |
                Permission.WRITE_ARTICLE |
                Permission.MODERATE_COMMENT |
                Permission.MODERATE_ARTICLE |
                Permission.MODERATE_USER |
                Permission.ASSIGN_MODERATOR
            )
        }

        for name, permissions in roles.items():
            role = Role.query.filter_by(name=name, enable=True).first()
            if role:
                if role.permissions != permissions:
                    role.update(permissions=permissions)
            else:
                role = Role(name=name, permissions=permissions, enable=True)
                db.session.add(role)
        db.session.commit()
