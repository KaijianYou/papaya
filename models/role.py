# -*- coding: utf-8 -*-


from app import db


class Permission:
    """
    # -------------------------------------------------------------------------
    # |        操  作        |      位  值       |         说  明             |
    # | 关注他人             | 0b00000001 (0x01) | 关注其他用户               |
    # | 在他人文章中发表评论 | 0b00000010 (0x02) | 在他人撰写的文章中发布评论 |
    # | 写文章               | 0b00000100 (0x04) | 写原创文章                 |
    # | 管理他人发表的评论   | 0b00001000 (0x08) | 查处他人发表的不当评论     |
    # | 管理员权限           | 0b10000000 (0x80) | 管理网站                   |
    # -------------------------------------------------------------------------
    """

    FOLLOW = 0x01
    COMMENT = 0x02
    WRITE_ARTICLES = 0x04
    MODERATE_COMMENTS = 0x08
    ADMINISTER = 0x80


class Role(db.Model):
    """
    # --------------------------------------------------------------------------------
    # | 用户角色 |       权  限       |          说明                                |
    # | 匿名     | 0b00000000 (0x00)  | 未登录的用户。在程序中只有阅读权限           |
    # | 用户     | 0b00000111 (0x07)  | 具有发布文章、发表评论和关注其他用户的权限。 |
    # |          |                    | 这是新用户的默认角色                         |
    # | 协管员   | 0b00001111 (0x0f)  | 增加审查不当评论的权限                       |
    # | 管理员   | 0b11111111 (0xff)  | 具有所有权限，包括修改其他用户所属角色的权限 |
    # --------------------------------------------------------------------------------
    """

    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<Role %s>' % self.name

    @staticmethod
    def insert_roles():
        roles = {
            'User':
                (Permission.FOLLOW |
                 Permission.COMMENT |
                 Permission.WRITE_ARTICLES, True),
            'Moderator':
                (Permission.FOLLOW |
                 Permission.COMMENT |
                 Permission.WRITE_ARTICLES |
                 Permission.MODERATE_COMMENTS, False),
            'Administrator':
                (0xff, False)
        }

        for role_name in roles:
            role = Role.query.filter_by(name=role_name).first()
            if role is None:
                role = Role(name=role_name)
            role.permissions = roles[role_name][0]
            role.default = roles[role_name][1]
            db.session.add(role)
        db.session.commit()
