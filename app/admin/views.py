from flask import render_template

from app.admin import admin


@admin.route('/')
def index():
    return render_template('admin/index.html')


@admin.route('/operation-logs')
def operation_log_list():
    return render_template('admin/operation_log_list.html')


@admin.route('/database-backups')
def db_backup_list():
    return render_template('admin/db_backup_list.html')
