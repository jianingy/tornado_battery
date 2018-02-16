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
from tornado_battery.controller import JSONController, ClientException
from tornado.testing import AsyncHTTPTestCase, gen_test
from tornado.web import Application as WebApplication
from ujson import dumps as json_encode
import pytest


class SimpleController(JSONController):

    def get(self):
        return self.reply(quote="may the force be with you")

    async def post(self):
        return self.reply(data=self.data)


class BailController(JSONController):

    def get(self):
        self.bail(503, reason="something wrong")


class ExceptionController(JSONController):

    def get(self):
        raise ClientException(reason="something wrong")


class TestController(AsyncHTTPTestCase):

    def get_app(self):
        app = WebApplication([
            (r"/", SimpleController),
            (r"/bail", BailController),
            (r"/exception", ExceptionController),
        ])
        return app

    def test_json_reply(self):
        response = self.fetch("/")
        assert response.body == b'{"quote":"may the force be with you"}'
        assert response.headers["Content-Type"] == "application/json; charset=UTF-8"

    def test_bail(self):
        response = self.fetch("/bail")
        assert response.code == 503
        assert response.body == b'{"reason":"something wrong"}'

    def test_json_request(self):
        data = json_encode(dict(x=1, y=2))
        headers = {
            "Content-Type": "application/json"
        }
        response = self.fetch("/", method="POST", body=data, headers=headers)
        assert response.body == b'{"data":{"x":1,"y":2}}'

    def test_json_request_no_content_type(self):
        data = json_encode(dict(x=1, y=2))
        response = self.fetch("/", method="POST", body=data)
        assert response.body == b'{"data":{}}'

    def test_json_request_invalid_json_data(self):
        data = "{Invalid JSON}"
        headers = {
            "Content-Type": "application/json"
        }
        response = self.fetch("/", method="POST", body=data, headers=headers)
        match = b'{"reason":"Request data must be in JSON format","status":400001}'
        assert response.body == match

    def test_exception(self):
        response = self.fetch("/exception")
        match = b'{"reason":"something wrong","status":400000}'
        assert response.body == match
