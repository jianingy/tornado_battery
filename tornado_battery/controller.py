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
from .exception import GeneralException, ClientException
from ujson import loads as json_decode, dumps as json_encode
from traceback import format_exception
import tornado.web


class InvalidJSONRequestData(ClientException):
    error_format = "Request data must be in JSON format"
    error_code = 400001


class JSONController(tornado.web.RequestHandler):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data = dict()

    def prepare(self):
        content_type = self.request.headers.get('Content-Type')

        if not self.request.body:
            return

        if not content_type:
            return

        if content_type.strip().lower().startswith('application/json'):
            try:
                self.data = json_decode(self.request.body)
            except:
                raise InvalidJSONRequestData()

    def reply(self, *args, **kwargs):
        self.set_header('Content-Type', 'application/json; charset=UTF-8')
        self.finish(json_encode(kwargs))

    def bail(self, status_code, *args, **kwargs):
        self.set_header('Content-Type', 'application/json; charset=UTF-8')
        self.set_status(status_code)
        self.finish(json_encode(kwargs))

    def write_error(self, status_code, **kwargs):
        if 'exc_info' in kwargs:
            retval = dict()
            exc_type, exc, trace = kwargs['exc_info']
            if exc.args and isinstance(exc.args[0], dict):
                retval["exc"] = exc.args[0]
            if isinstance(exc, GeneralException):
                retval["reason"] = exc.message
            else:
                retval["reason"] = str(exc)
            if isinstance(exc, ClientException):
                self.set_status(400)
            elif isinstance(exc, ClientException):
                self.set_status(500)
            if hasattr(exc, "error_code"):
                retval["status"] = exc.error_code
            else:
                self.set_status(500)
                retval["status"] = 500000
            if tornado.options.options.debug:
                retval['traceback'] = format_exception(exc_type, exc, trace)
            self.reply(**retval)
        else:
            self.set_status(status_code)
            self.reply(reason="no detail information")
