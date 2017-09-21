# -*- coding: utf-8 -*-


from flask import render_template

from app.admin import admin


@admin.route('/login')
def login():
    return render_template('admin/auth/login.html')


@admin.route('/logout')
def logout():
    return render_template('admin/index.html')
