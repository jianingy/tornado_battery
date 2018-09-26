from marshmallow import Schema, fields

from tornado.options import options
from tornado.testing import AsyncHTTPTestCase
from tornado.web import Application as WebApplication, RequestHandler
from ujson import dumps as json_encode, loads as json_decode

from tornado_battery.exception import ServerException
from tornado_battery.schema import schema


class User(Schema):

    name = fields.String(required=True)
    age = fields.Integer(required=True)
    alias = fields.Nested(fields.String, loads_from='alias[]')


user_schema = User(strict=True)


class JSONSchemaHandler(RequestHandler):

    @schema(json=user_schema)
    async def post(self, *, json):
        assert 'name' in json
        assert 'age' in json
        assert json['name'] == 'john'
        assert json['age'] == 20


class FormSchemaHandler(RequestHandler):

    @schema(form=user_schema)
    async def post(self, *, form):
        assert 'name' in form
        assert 'age' in form
        assert form['name'] == 'john'
        assert form['age'] == 20


class QuerySchemaHandler(RequestHandler):

    @schema(query=user_schema)
    async def get(self, *, query):
        assert 'name' in query
        assert 'age' in query
        assert query['name'] == 'john'
        assert query['age'] == 20


class ReplySchemaHandler(RequestHandler):

    @schema(reply=user_schema)
    async def get(self):
        return dict(data=dict(name='john', age=20))


class ReplySchemaCustomHandler(RequestHandler):

    @schema(reply=True)
    async def get(self):
        return dict(name='john', age=20)


class ServerErrorHandler(RequestHandler):

    @schema(reply=True, error=True)
    async def get(self):
        raise ServerException(reason='server error')


def custom_error_handler(handler, exc):
    handler.set_status(599)
    return dict(name=str(exc))


class CustomServerErrorHandler(RequestHandler):

    @schema(reply=True, error=custom_error_handler)
    async def get(self):
        raise ServerException(reason='server error')


class WildCustomServerErrorHandler(RequestHandler):
    @schema(reply=True, error=custom_error_handler)
    async def get(self):
        return dict(v=1/0)


class UnhandleServerErrorHandler(RequestHandler):

    @schema(reply=True)
    async def get(self):
        raise ServerException(reason='server error')


class WildUnhandleServerErrorHandler(RequestHandler):

    @schema(reply=True)
    async def get(self):
        return dict(v=1/0)


class TestSchema(AsyncHTTPTestCase):

    def get_app(self):
        app = WebApplication([
            (r'/', ReplySchemaHandler),
            (r'/error', ServerErrorHandler),
            (r'/error/custom', CustomServerErrorHandler),
            (r'/error/custom/wild', WildCustomServerErrorHandler),
            (r'/error/unhandle', UnhandleServerErrorHandler),
            (r'/error/unhandle/wild', WildUnhandleServerErrorHandler),
            (r'/custom', ReplySchemaCustomHandler),
            (r'/json', JSONSchemaHandler),
            (r'/form', FormSchemaHandler),
            (r'/query', QuerySchemaHandler),
        ])
        return app

    def test_json_schema(self):
        data = json_encode(dict(name='john', age=20))
        headers = {
            'Content-Type': 'application/json',
        }
        response = self.fetch('/json', method='POST', body=data,
                              headers=headers)
        assert response.code == 200

    def test_json_schema_without_header(self):
        data = json_encode(dict(name='john', age=20))
        response = self.fetch('/json', method='POST', body=data,
                              raise_error=False)
        assert response.code == 500

    def test_json_schema_invalid_json(self):
        headers = {
            'Content-Type': 'application/json',
        }
        response = self.fetch('/json', method='POST', body='{a:1}',
                              headers=headers, raise_error=False)
        assert response.code == 500

    def test_form_schema(self):
        data = 'name=john&age=20&alias[]=jj&alias[]=kk'
        response = self.fetch('/form', method='POST', body=data)
        assert response.code == 200

    def test_query_schema(self):
        data = 'name=john&age=20&alias[]=jj&alias[]=kk'
        response = self.fetch(f'/query?{data}', method='GET')
        assert response.code == 200

    def test_reply_schema(self):
        response = self.fetch(f'/', method='GET')
        expect = (
            b'{"code": 0, "msg": "", "data": {"age": 20, "name": "john"}}',
            b'{"code": 0, "msg": "", "data": {"name": "john", "age": 20}}',
        )
        assert response.code == 200
        assert response.body in expect

    def test_reply_schema_custom(self):
        response = self.fetch(f'/custom', method='GET')
        expect = (
            b'{"age": 20, "name": "john"}',
            b'{"name": "john", "age": 20}',
        )
        assert response.code == 200
        assert response.body in expect

    def test_reply_schema_default_error(self):
        response = self.fetch(f'/error', method='GET')
        data = json_decode(response.body)
        assert response.code == 500
        assert data['msg'] == 'server error'
        assert data['code'] == 500000
        assert 'traceback' not in data

    def test_reply_schema_default_error_with_traceback(self):
        options.debug = True
        response = self.fetch(f'/error', method='GET')
        options.debug = False
        data = json_decode(response.body)
        assert response.code == 500
        assert data['msg'] == 'server error'
        assert data['code'] == 500000
        assert 'traceback' in data

    def test_reply_schema_custom_error(self):
        response = self.fetch(f'/error/custom', method='GET')
        data = json_decode(response.body)
        assert response.code == 599
        assert data['name'] == 'server error'

    def test_reply_schema_custom_error_wild(self):
        response = self.fetch(f'/error/custom/wild', method='GET')
        data = json_decode(response.body)
        assert response.code == 599
        assert data['name'] == 'division by zero'

    def test_reply_schema_unhandle_error(self):
        response = self.fetch(f'/error/unhandle', method='GET')
        assert response.code == 500

    def test_reply_schema_unhandle_error_wild(self):
        response = self.fetch(f'/error/unhandle/wild', method='GET')
        assert response.code == 500
