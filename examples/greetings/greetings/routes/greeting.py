# -*- coding: UTF-8 -*-
from . import route
from marshmallow import Schema, fields
from tornado.web import RequestHandler
from tornado_battery.schema import schema
from tornado_battery.postgres import with_postgres


class Quote(Schema):

    quote = fields.String(dump_to='quote')


class QuoteList(Schema):

    quotes = fields.Nested(Quote, many=True)


@route('/api/v1/greetings')
class AddController(RequestHandler):

    @schema(reply=QuoteList(strict=True))
    @with_postgres(name='slave')
    async def get(self, db):
        async with db.cursor() as cursor:
            await cursor.execute('SELECT quote FROM quotes ORDER BY RANDOM()')
            rows = await cursor.fetchall()
        columns = tuple(map(lambda x: x.name, cursor.description))
        rows = map(lambda x: dict(zip(columns, x)), rows)
        return dict(code=0, msg='ok', data=dict(quotes=rows))

    @schema(json=Quote(strict=True), reply=True)
    @with_postgres(name='master')
    async def post(self, db, json):
        async with db.cursor() as cursor:
            await cursor.execute('INSERT INTO quotes(quote) VALUES(%(quote)s)',
                                 dict(quote=json['quote']))
        return dict(status='OK', quote=json['quote'])
