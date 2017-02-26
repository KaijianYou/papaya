# -*- coding: utf-8 -*-


"""
@Description: 
@Version: 
@Software: PyCharm
@Author: youkaijian
@Date: 2017/02/23
"""


from flask import Blueprint
from flask_login import login_required
from ..decorators import admin_required, permission_required
from ..models import Permission


main = Blueprint('main', __name__)


@main.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)


from . import views, errors
