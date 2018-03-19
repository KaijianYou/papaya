from flask import jsonify


class JSONUtil(object):
    @classmethod
    def generate_error_json(cls, error=None):
        data = {'success': False}
        if error:
            data['error'] = {
                'code': error.code,
                'message': error.message
            }
        return jsonify(data)

    @classmethod
    def generate_result_json(cls, result_dict=None):
        if result_dict and not isinstance(result_dict, dict):
            raise ValueError('参数类型错误')
        result_dict['success'] = True
        return jsonify(result_dict)
