from datetime import datetime

from sqlalchemy.orm.interfaces import MapperExtension
from sqlalchemy.orm.attributes import set_attribute

from app import db


class ModelUpdateExtension(MapperExtension):
    def before_update(self, mapper, connection, instance):
        if hasattr(instance, 'update_datetime'):
            instance.update_datetime = datetime.utcnow()


class BaseMixin(object):
    __mapper_args__ = {
        'extension': ModelUpdateExtension()
    }

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    create_datetime = db.Column(db.DateTime(False), default=datetime.utcnow)
    update_datetime = db.Column(db.DateTime(False), default=datetime.utcnow)
    enable = db.Column(db.Boolean, default=True)

    def update(self, **kwargs):
        for attr in kwargs:
            if attr in self._columns() and kwargs[attr] is not None:
                set_attribute(self, attr, kwargs[attr])
        db.session.commit()
        return self

    @classmethod
    def find_by_id(cls, id, must_enable=True):
        query = cls.query
        if must_enable:
            query = query.filter_by(enable=True)
        return query.filter_by(id=id).first()

    @classmethod
    def _columns(cls):
        return set(column.key for column in cls.__table__.columns)
