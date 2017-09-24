# -*- coding: utf-8 -*-


from flask import request
from flask import render_template
from flask import jsonify

from app.main import main
from utils.error import BaseError


@main.app_errorhandler(403)
def forbidden(e):
    if request.accept_mimetypes.accept_json and \
            not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'forbidden'})
        response.status_code = 403
        return response
    return render_template('error/403.html'), 403


@main.app_errorhandler(404)
def page_not_found(e):
    if request.accept_mimetypes.accept_json and \
            not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'not found'})
        response.status_code = 404
        return response
    return render_template('error/404.html'), 404


@main.app_errorhandler(500)
def internal_server_error(e):
    if request.accept_mimetypes.accept_json and \
            not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'internal server error'})
        response.status_code = 500
        return response
    return render_template('error/500.html'), 500


class VoteArticleError(object):
    ArticleNotExist = BaseError(0, '文章不存在')
    VoteNotExist = BaseError(0, '用户没有赞或踩过这篇文章')
    TypeError = BaseError(0, '操作类型错误')
    AlreadyUpVoted = BaseError(0, '已经赞过这篇文章')
    NotUpVoted = BaseError(0, '没有赞过这篇文章')
    AlreadyDownVoted = BaseError(0, '已经踩过这篇文章')
    NotDownVoted = BaseError(0, '没有踩过这篇文章')
