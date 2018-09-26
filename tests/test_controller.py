# -*- coding: utf-8 -*-
#
#        H A P P Y    H A C K I N G !
#              _____               ______
#     ____====  ]OO|_n_n__][.      |    |
#    [________]_|__|________)<     |YANG|
#     oo    oo  'oo OOOO-| oo\\_   ~o~~o~
# +--+--+--+--+--+--+--+--+--+--+--+--+--+
#               Jianing Yang @ 16 Feb, 2018
#
from tornado.options import options
from tornado.testing import AsyncHTTPTestCase
from tornado.web import Application as WebApplication
from tornado_battery.controller import JSONController
from tornado_battery.exception import ClientException, ServerException
from ujson import dumps as json_encode
from unittest import mock


class SimpleController(JSONController):

    def get(self):
        return self.reply(quote='may the force be with you')

    async def post(self):
        return self.reply(data=self.data)

    def put(self):
        return self.reply(quote=self.get_data('quote', 'no data'))

    def patch(self):
        return self.reply(quote=self.get_data('quote', 'no data', strip=False))


class BailController(JSONController):

    def get(self):
        self.bail(503, reason='something wrong')


class ClientExceptionController(JSONController):

    def get(self):
        raise ClientException(reason='something wrong')


class ServerExceptionController(JSONController):

    def get(self):
        raise ServerException(reason='something wrong')


class PythonExceptionController(JSONController):

    def get(self):
        raise ValueError('a value error')


class ExceptionWithCode(ClientException):
    http_status_code = 403


class UnauthorizedController(JSONController):

    def get(self):
        raise ExceptionWithCode()


class TestController(AsyncHTTPTestCase):

    def get_app(self):
        app = WebApplication([
            (r'/', SimpleController),
            (r'/bail', BailController),
            (r'/exception/client', ClientExceptionController),
            (r'/exception/server', ServerExceptionController),
            (r'/exception/python', PythonExceptionController),
            (r'/exception/403', UnauthorizedController),
        ])
        return app

    def test_json_reply(self):
        response = self.fetch('/')
        assert response.body == b'{"quote":"may the force be with you"}'
        assert (response.headers['Content-Type'] ==
                'application/json; charset=UTF-8')

    def test_bail(self):
        response = self.fetch('/bail')
        assert response.code == 503
        assert response.body == b'{"reason":"something wrong"}'

    def test_json_request(self):
        data = json_encode(dict(x=1, y=2))
        headers = {
            'Content-Type': 'application/json',
        }
        response = self.fetch('/', method='POST', body=data, headers=headers)
        assert response.body == b'{"data":{"x":1,"y":2}}'

    def test_get_data(self):
        data = json_encode(dict(quote='hello, world'))
        headers = {
            'Content-Type': 'application/json',
        }
        response = self.fetch('/', method='PUT', body=data, headers=headers)
        assert response.body == b'{"quote":"hello, world"}'

    def test_get_data_num(self):
        data = json_encode(dict(quote=1984))
        headers = {
            'Content-Type': 'application/json',
        }
        response = self.fetch('/', method='PUT', body=data, headers=headers)
        assert response.body == b'{"quote":1984}'

    def test_get_data_empty(self):
        data = json_encode(dict(non='hello, world'))
        headers = {
            'Content-Type': 'application/json',
        }
        response = self.fetch('/', method='PUT', body=data, headers=headers)
        assert response.body == b'{"quote":"no data"}'

    def test_get_data_strip(self):
        data = json_encode(dict(quote='\t\r\n vvv  \r\t\n  '))
        headers = {
            'Content-Type': 'application/json',
        }
        response = self.fetch('/', method='PUT', body=data, headers=headers)
        assert response.body == b'{"quote":"vvv"}'

    def test_get_data_dont_strip(self):
        data = json_encode(dict(quote='\t\r\n vvv  \r\t\n  '))
        headers = {
            'Content-Type': 'application/json',
        }
        response = self.fetch('/', method='PATCH', body=data, headers=headers)
        assert response.body == b'{"quote":"\\t\\r\\n vvv  \\r\\t\\n  "}'

    def test_json_request_no_content_type(self):
        data = json_encode(dict(x=1, y=2))
        headers = {
            'Content-Type': '',
        }
        response = self.fetch('/', method='POST', body=data, headers=headers)
        assert response.body == b'{"data":{}}'

    def test_json_request_invalid_json_data(self):
        data = '{Invalid JSON}'
        headers = {
            'Content-Type': 'application/json',
        }
        response = self.fetch('/', method='POST', body=data, headers=headers)
        match = (b'{"reason":"Request data must be in JSON format",'
                 b'"status":400001}')
        assert response.body == match

    def test_client_exception(self):
        response = self.fetch('/exception/client')
        match = b'{"reason":"something wrong","status":400000}'
        assert response.body == match

    def test_server_exception(self):
        response = self.fetch('/exception/server')
        match = b'{"reason":"something wrong","status":500000}'
        assert response.body == match

    def test_python_exception(self):
        response = self.fetch('/exception/python')
        match = b'{"reason":"a value error","status":500000}'
        assert response.body == match

    def test_http_code(self):
        response = self.fetch('/exception/403')
        assert response.code == 403

    def test_allow_origin(self):
        response = self.fetch('/')
        assert 'Access-Control-Allow-Origin' not in response.headers

        with mock.patch.object(options.mockable(), 'debug', True):
            response = self.fetch('/')
            assert response.headers['Access-Control-Allow-Origin'] == '*'
