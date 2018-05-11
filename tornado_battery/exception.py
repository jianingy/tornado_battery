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


class GeneralException(Exception):
    error_format = "application exception occurred: %(reason)s"

    def __init__(self, message: str=None, **kwargs):
        self.kwargs = kwargs

        if not message:
            try:
                message = self.error_format % self.kwargs
            except KeyError:
                message = ("cannot format exception message: '%s'" %
                           self.error_format)

        if "error_code" in kwargs:
            self.error_code = kwargs["error_code"]

        self.message = message
        super().__init__(message)


class ClientException(GeneralException):
    error_format = "%(reason)s"
    error_code = 400000


class ServerException(GeneralException):
    error_format = "%(reason)s"
    error_code = 500000
