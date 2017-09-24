# -*- coding: utf-8 -*-


from flask import jsonify


class JSONUtil(object):
    @classmethod
    def generate_error_response(cls, error=None, status_code=200):
        data = {'success': False}
        if error:
            data['error'] = {
                'code': error.code,
                'message': error.message
            }
        response = jsonify(data)
        response.status_code = status_code
        return response

    @classmethod
    def generate_success_response(cls, status_code=200):
        response = jsonify({
            'success': True
        })
        response.status_code = status_code
        return response

    @classmethod
    def generate_result_response(cls, result_dict, status_code=200):
        if not isinstance(result_dict, dict):
            raise ValueError('参数类型错误')
        if 'success' not in result_dict:
            result_dict['success'] = True
        response = jsonify(result_dict)
        response.status_code = status_code
        return response
