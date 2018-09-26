# -*- coding: utf-8 -*-
#
#        H A P P Y    H A C K I N G !
#              _____               ______
#     ____====  ]OO|_n_n__][.      |    |
#    [________]_|__|________)<     |YANG|
#     oo    oo  'oo OOOO-| oo\\_   ~o~~o~
# +--+--+--+--+--+--+--+--+--+--+--+--+--+
#               Jianing Yang @ 17 Feb, 2018
#
from tornado_battery.postgres import register_postgres_options, with_postgres
from tornado_battery.postgres import PostgresConnector, PostgresConnectorError
import pytest

pytestmark = pytest.mark.asyncio
register_postgres_options('test', 'postgres://test:test@127.0.0.1/test')


@pytest.fixture
async def postgres():
    from tornado_battery.postgres import connect_postgres
    db = PostgresConnector.instance('test')
    connect = connect_postgres('test')
    await connect()
    return db


async def test_select(postgres):

    @with_postgres(name='test')
    async def _select(db):
        async with db.cursor() as cursor:
            await cursor.execute('SELECT 1')
            value = await cursor.fetchone()
            return value

    assert (await _select()) == (1,)


async def test_decorator_duplicated(postgres):

    @with_postgres(name='test')
    async def _select(db):
        async with db.cursor() as cursor:
            await cursor.execute('SELECT 1')
            value = await cursor.fetchone()
            return value
    with pytest.raises(PostgresConnectorError):
        await _select(db=None)


async def test_no_connection():
    match = r'^no connection of noconn found$'
    with pytest.raises(PostgresConnectorError, match=match):
        PostgresConnector.instance('noconn').connection()


async def test_invalid_connection_scheme():
    from tornado.options import options
    options.postgres_test_uri = 'test://'
    match = r' is not a postgres connection scheme$'
    with pytest.raises(PostgresConnectorError, match=match):
        await PostgresConnector.instance('test').connect()


async def test_option_name():
    from tornado_battery.postgres import option_name

    assert option_name('master', 'uri') == 'postgres-master-uri'
    assert option_name('slave', 'uri') == 'postgres-slave-uri'
