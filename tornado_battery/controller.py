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
from ujson import loads as json_decode, dumps as json_encode
from tornado.options import options
from traceback import format_exception

import tornado.web
import warnings

from .exception import GeneralException, ClientException, ServerException

warnings.warn('tornado_battery.controller is deprecated and'
              ' it will be removed in the future',
              DeprecationWarning)


class InvalidJSONRequestData(ClientException):
    error_format = 'Request data must be in JSON format'
    error_code = 400001


class JSONController(tornado.web.RequestHandler):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data = dict()

    def prepare(self):
        super().prepare()
        content_type = self.request.headers.get('Content-Type')

        if not self.request.body:
            return

        if not content_type:
            return

        if content_type.strip().lower().startswith('application/json'):
            try:
                self.data = json_decode(self.request.body)
            except ValueError as e:
                raise InvalidJSONRequestData() from e

    def reply(self, *args, **kwargs):
        self.set_header('Content-Type', 'application/json; charset=UTF-8')
        self.finish(json_encode(kwargs))

    def bail(self, status_code: int, *args, **kwargs):
        self.set_header('Content-Type', 'application/json; charset=UTF-8')
        self.set_status(status_code)
        self.finish(json_encode(kwargs))

    def options(self, *args, **kwargs):
        if options.debug:
            self.set_header('Allow', 'POST, GET, PUT, DELETE, OPTIONS, PATCH')

    def set_default_headers(self, *args, **kwargs):
        super().set_default_headers(*args, **kwargs)
        if options.debug:
            self.set_header('Access-Control-Allow-Origin', '*')
            self.set_header('Access-Control-Allow-Methods',
                            'POST, GET, PUT, DELETE, OPTIONS, PATCH')
            self.set_header('Access-Control-Max-Age', '3600')
            self.set_header('Access-Control-Allow-Headers',
                            'Content-Type, Access-Control-Allow-Headers')

    def get_data(self, name, default, strip=True):
        v = self.data.get(name, default)
        if strip and isinstance(v, str):
            v = v.strip()
        return v

    def write_error(self, status_code: int, **kwargs):
        if 'exc_info' in kwargs:
            retval = dict()
            exc_type, exc, trace = kwargs['exc_info']
            if isinstance(exc, GeneralException):
                retval['reason'] = exc.message
            else:
                retval['reason'] = str(exc)
            if isinstance(exc, ClientException):
                self.set_status(400)
            elif isinstance(exc, ServerException):
                self.set_status(500)
            if hasattr(exc, 'http_status_code'):
                self.set_status(exc.http_status_code)
            if hasattr(exc, 'error_code'):
                retval['status'] = exc.error_code
            else:
                retval['status'] = 500000
            if hasattr(options, 'debug') and options.debug:
                retval['traceback'] = format_exception(exc_type, exc, trace)
            self.reply(**retval)
        else:
            self.set_status(status_code)
            self.reply(reason='no detail information')
