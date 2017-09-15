# -*- coding: utf-8 -*-


from uuid import uuid1


class UUIDUtil(object):

    @classmethod
    def generate_slug(cls, length=8):
        hash_value = hash(str(uuid1()))
        if hash_value < 0:
            hash_value *= -1
        return str(hash_value)[0:length]

    @classmethod
    def generate_uuid(cls):
        return str(uuid1())
