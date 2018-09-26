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
from tornado.testing import AsyncHTTPTestCase
from tornado_battery.extra import try_get_value, CORSHandlerMixin
from tornado_battery.schema import schema
from tornado.web import Application as WebApplication, RequestHandler
from tornado.options import options
import pytest


@pytest.fixture
def data():

    return {
        '1': {
            'A': {
                'a': 'value',
            },
            'B': 'Bvalue',
        },
    }


def test_last_node(data):
    assert try_get_value(data, '1.A.a', None) == 'value'


def test_last_non_exists(data):
    assert try_get_value(data, '1.A.b', 'n/a') == 'n/a'


def test_middle_non_exists(data):
    assert try_get_value(data, '1.c.a', 'n/a') == 'n/a'


def test_middle_node(data):
    assert try_get_value(data, '1.B', 'n/a') == 'Bvalue'


def test_empty(data):
    assert try_get_value(data, '', 'n/a') == 'n/a'


def test_non_dict():
    assert try_get_value(1, '', 'n/a') == 'n/a'


class CORSHandler(CORSHandlerMixin, RequestHandler):

    @schema(reply=True)
    async def get(self):
        return dict(name='john', age=20)

    def options(self):
        super().options()


class TestApp(AsyncHTTPTestCase):

    def get_app(self):
        app = WebApplication([
            (r'/cors', CORSHandler),
        ])
        return app

    def test_cors_with_debug(self):
        options.debug = True
        response = self.fetch('/cors', method='GET')
        options.debug = False
        headers = response.headers
        assert headers['Access-Control-Allow-Origin'] == '*'
        assert (headers['Access-Control-Allow-Methods'] ==
                'GET, POST, PUT, DELETE, OPTIONS, HEAD, PATCH')
        assert headers['Access-Control-Max-Age'] == '3600'
        assert (headers['Access-Control-Allow-Headers'] ==
                'Content-Type, Access-Control-Allow-Headers')
        assert response.code == 200
        options.debug = True
        response = self.fetch('/cors', method='OPTIONS')
        headers = response.headers
        options.debug = False
        assert headers['Allow'] == 'POST, GET, PUT, DELETE, OPTIONS, PATCH'

    def test_cors(self):
        response = self.fetch('/cors', method='GET')
        headers = response.headers
        assert 'Access-Control-Allow-Origin' not in headers
        assert 'Access-Control-Allow-Methods' not in headers
        assert 'Access-Control-Max-Age' not in headers
        assert 'Access-Control-Allow-Headers' not in headers
        assert response.code == 200
        response = self.fetch(f'/cors', method='OPTIONS')
        assert 'Allow' not in headers
