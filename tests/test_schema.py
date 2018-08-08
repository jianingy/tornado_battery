from marshmallow import Schema, fields

from tornado.testing import AsyncHTTPTestCase
from tornado.web import Application as WebApplication, RequestHandler
from ujson import dumps as json_encode

from tornado_battery.schema import schema


class User(Schema):

    name = fields.String(required=True)
    age = fields.Integer(required=True)


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


class TestSchema(AsyncHTTPTestCase):

    def get_app(self):
        app = WebApplication([
            (r'/', ReplySchemaHandler),
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

    def test_form_schema(self):
        data = 'name=john&age=20'
        response = self.fetch('/form', method='POST', body=data)
        assert response.code == 200

    def test_query_schema(self):
        data = 'name=john&age=20'
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
