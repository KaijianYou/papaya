# -*- coding: utf-8 -*-


from functools import wraps
from threading import Thread

from flask import abort
from flask_login import current_user

from models.role import Permission


def permission_required(permission):
    """检查用户权限"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not current_user.can(permission):
                abort(403)
            return func(*args, **kwargs)
        return wrapper
    return decorator


def admin_required(func):
    return permission_required(Permission.ADMINISTER)(func)


def async_task(func):
    @wraps(func)
    def decorator(*args, **kwargs):
        thread = Thread(target=func, args=args, kwargs=kwargs)
        thread.start()
    return decorator
