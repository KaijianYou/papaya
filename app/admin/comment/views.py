from flask import render_template, current_app, request

from app.admin import admin
from models.comment import Comment


@admin.route('/comments')
def comment_list():
    page = request.args.get('page', default=1, type=int)
    per_page = current_app.config['COMMENTS_PER_PAGE']
    pagination = Comment.query.paginate(page, per_page, error_out=False)
    comments = pagination.items
    return render_template('comment_list.html',
                           comments=comments,
                           pagination=pagination)
