# -*- coding: utf-8 -*-


"""
@Description: 
@Version: 
@Software: PyCharm
@Author: youkaijian
@Date: 2017/02/23
"""


from flask import Blueprint


main = Blueprint('main', __name__)


from . import views, errors
