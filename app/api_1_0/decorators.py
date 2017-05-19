# -*- coding: utf-8 -*-


from functools import wraps

from app.models import Permission
from app.api_1_0.errors import forbidden


def permission_required(permissions):
    def decorator(func):
        @wraps(func)
        def wrapper(*argc, **kwargs):
            if not g.current_user.can(permissions):
                return forbidden('permission denied')
            return func(*argc, **kwargs)
        return wrapper
    return decorator


def admin_required(func):
    return permission_required(Permission.ADMINISTER)(func)
