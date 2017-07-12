# -*- coding: utf-8 -*-


from urllib.parse import urlparse, urljoin

from flask import request


class RequestUtils(object):

    @staticmethod
    def get_ip_address():
        return request.environ.get('HTTP_X_REAL_IP', request.remote_addr) or '127.0.0.1'

    @staticmethod
    def is_safe_url(target):
        ref_url = urlparse(request.host_url)
        test_url = urlparse(urljoin(request.host_url, target))
        return test_url.scheme in ('http', 'https') and \
               ref_url.netloc == test_url.netloc