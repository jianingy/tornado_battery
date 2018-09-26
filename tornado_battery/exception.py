# -*- coding: utf-8 -*-
#
#        H A P P Y    H A C K I N G !
#              _____               ______
#     ____====  ]OO|_n_n__][.      |    |
#    [________]_|__|________)<     |YANG|
#     oo    oo  'oo OOOO-| oo\\_   ~o~~o~
# +--+--+--+--+--+--+--+--+--+--+--+--+--+
#               Jianing Yang @  8 Feb, 2018
#

import warnings

_error_codes = []


class _MetaException(type):

    def __new__(cls, name, bases, body):
        qualname = body['__qualname__']
        new_class = type.__new__(cls, name, bases, body)
        if new_class.error_code in _error_codes:
            warnings.warn(f'{qualname} has duplicated error_code',
                          stacklevel=2)
        else:
            _error_codes.append(new_class.error_code)
        return new_class


class GeneralException(Exception, metaclass=_MetaException):

    error_code = 1000
    error_format = 'application exception occurred: %(reason)s'
    http_status_code = 500

    def __init__(self, message: str=None, **kwargs):
        self.kwargs = kwargs

        if not message:
            try:
                message = self.error_format % self.kwargs
            except KeyError:
                message = f'cannot format exception: {self.error_format}'

        self.message = message
        super().__init__(message)


class ClientException(GeneralException):
    error_format = '%(reason)s'
    error_code = 400000
    http_status_code = 400


class ServerException(GeneralException):
    error_format = '%(reason)s'
    error_code = 500000
    http_status_code = 500
