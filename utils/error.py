# -*- coding: utf-8 -*-


class BaseError(object):

    def __init__(self, code, message):
        self.code = code
        self.message = message
