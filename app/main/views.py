# -*- coding: utf-8 -*-


"""
@Description: 
@Version: 
@Software: PyCharm
@Author: youkaijian
@Date: 2017/02/24
"""


from datetime import datetime
from flask import render_template
from . import main


# 如果不指定 methods 参数，则默认将函数注册为 GET 请求的处理程序
@main.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html', current_time=datetime.utcnow())
