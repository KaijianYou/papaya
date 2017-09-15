# -*- coding: utf-8 -*-


from urllib.parse import urljoin

from flask import current_app
import qiniu


class QiniuUtils(object):

    app = current_app._get_current_object()
    access_key = app.config.get('QINIU_ACCESS_KEY', '')
    secret_key = app.config.get('QINIU_SECRET_KEY', '')
    bucket = app.config.get('QINIU_BUCKET_NAME', '')
    domain = app.config.get('QINIU_DOMAIN_NAME', '')
    auth = qiniu.Auth(access_key, secret_key)

    @classmethod
    def generate_upload_token(cls):
        return cls.auth.upload_token(cls.bucket)

    @classmethod
    def save(cls, key, data, mime_type='application/octet-stream'):
        upload_token = cls.generate_upload_token()
        ret, info = qiniu.put_data(upload_token, key, data, key, mime_type=mime_type)
        print(ret)
        print(info)

    @classmethod
    def delete(cls, key):
        bucket_manager = qiniu.BucketManager(cls.auth)
        ret, info = bucket_manager.delete(cls.bucket, key)
        print(ret)
        print(info)

    @classmethod
    def url(cls, key):
        if cls.domain:
            base_url = 'http://' + cls.domain
        else:
            base_url = 'http://' + cls.bucket + '.static.com'
        return urljoin(base_url, key)
