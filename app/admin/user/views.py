from flask import render_template, request, current_app

from app.admin import admin
from models.user import User
from models.role import Role


@admin.route('/users')
@admin.route('/users/<string:role_name>')
def user_list(role_name=None):
    page = request.args.get('page', default=1, type=int)
    per_page = current_app.config['USERS_PER_PAGE']
    if role_name:
        pagination = User.query.paginate(page, per_page, error_out=False)
    else:
        role = Role.query.filter_by(name=role_name).first_or_404()
        pagination = role.users.paginate(page, per_page, error_out=False)
    users = pagination.items
    return render_template('user_list.html',
                           users=users,
                           pagination=pagination)


@admin.route('/user/profile')
def user_profile():
    return render_template('user_profile.html')
