# -*- coding: utf-8 -*-


"""
@Description: 
@Version: 
@Software: PyCharm
@Author: youkaijian
@Date: 2017/02/24
"""


from flask import Blueprint


auth = Blueprint('auth', __name__)


from . import views
