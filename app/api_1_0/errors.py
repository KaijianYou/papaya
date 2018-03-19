from flask import jsonify

from app.api_1_0 import api


def bad_request(message):
    response = jsonify({'error': 'bad_request', 'message': message})
    response.status_code = 400
    return response


def unauthorized(message):
    response = jsonify({'error': 'unauthorized', 'message': message})
    response.status_code = 401
    return response


def forbidden(message):
    response = jsonify({'error': 'forbidden', 'message': message})
    response.status_code = 403
    return response


def not_found(message):
    response = jsonify({'error': 'not found', 'message': message})
    response.status_code = 404
    return response


def method_not_allowed(message):
    response = jsonify({'error': 'method not allowed', 'messsage': message})
    response.status_code = 405
    return response


@api.errorhandler(ValueError)
def value_error(e):
    return bad_request((e.args[0]))
