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
from tornado_battery.mysql import register_mysql_options, with_mysql
from tornado_battery.mysql import MysqlConnector, MysqlConnectorError
from pymysql.err import IntegrityError
import pytest
import logging

pytestmark = pytest.mark.asyncio
register_mysql_options('test',
                       'mysql://root@127.0.0.1:3306/test?charset=utf8mb4')
logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger('test_mysql')


@pytest.fixture
async def mysql():
    from tornado_battery.mysql import connect_mysql
    db = MysqlConnector.instance('test')
    connect = connect_mysql('test')
    await connect()

    LOG.info('connect success!')

    @with_mysql(name='test')
    async def _init(db):
        async with db.cursor() as cursor:
            await cursor.execute('CREATE TABLE IF NOT EXISTS '
                                 'test(id SERIAL PRIMARY KEY, x INT, y INT, '
                                 'UNIQUE KEY (x, y));')
            await cursor.execute('TRUNCATE TABLE test')
            await cursor.execute('INSERT INTO test(x, y) VALUES(1, 1)')
            await cursor.execute('INSERT INTO test(x, y) VALUES(1, 2)')
    await _init()

    return db


async def test_select(mysql):

    @with_mysql(name='test')
    async def _select(db):
        async with db.cursor() as cursor:
            await cursor.execute('SELECT 1')
            value = await cursor.fetchone()
            return value

    assert (await _select()) == (1,)


async def test_error_transaction(mysql):

    @with_mysql(name='test')
    async def _insert(db):
        async with db.cursor() as cursor:
            await cursor.execute('BEGIN')
            await cursor.execute('INSERT INTO test(x, y) VALUES(2, 2)')
            await cursor.execute('INSERT INTO test(x, y) VALUES(1, 1)')
            await cursor.execute('COMMIT')

    @with_mysql(name='test')
    async def _select(db):
        async with db.cursor() as cursor:
            await cursor.execute('SELECT * FROM test WHERE x = 2 AND y = 2')
            value = await cursor.fetchone()
        return value

    with pytest.raises(IntegrityError):
        await _insert()

    assert (await _select()) is None


async def test_rollback_transaction(mysql):

    @with_mysql(name='test')
    async def _insert(db):
        async with db.cursor() as cursor:
            await cursor.execute('BEGIN')
            await cursor.execute('INSERT INTO test(x, y) VALUES(3, 3)')
            await cursor.execute('INSERT INTO test(x, y) VALUES(3, 4)')
            await cursor.execute('ROLLBACK')

    @with_mysql(name='test')
    async def _select(db):
        async with db.cursor() as cursor:
            await cursor.execute('SELECT * FROM test WHERE x = 2 AND y = 2')
            value = await cursor.fetchone()
        return value

    await _insert()
    assert (await _select()) is None


async def test_commit_transaction(mysql):

    @with_mysql(name='test')
    async def _insert(db):
        async with db.cursor() as cursor:
            await cursor.execute('BEGIN')
            await cursor.execute('INSERT INTO test(x, y) VALUES(4, 3)')
            await cursor.execute('INSERT INTO test(x, y) VALUES(4, 4)')
            await cursor.execute('COMMIT')

    @with_mysql(name='test')
    async def _select(db):
        async with db.cursor() as cursor:
            await cursor.execute('SELECT * FROM test WHERE x = 3')
            value = await cursor.fetchone()
        return value

    await _insert()


async def test_decorator_duplicated(mysql):

    @with_mysql(name='test')
    async def _select(db):
        async with db.cursor() as cursor:
            await cursor.execute('SELECT 1')
            value = await cursor.fetchone()
            return value
    with pytest.raises(MysqlConnectorError):
        await _select(db=None)


async def test_no_connection():
    match = r'^no connection of noconn found$'
    with pytest.raises(MysqlConnectorError, match=match):
        MysqlConnector.instance('noconn').connection()


async def test_invalid_connection_scheme():
    from tornado.options import options
    options.mysql_test_uri = 'test://'
    match = r' is not a mysql connection scheme$'
    with pytest.raises(MysqlConnectorError, match=match):
        await MysqlConnector.instance('test').connect()


async def test_option_name():
    from tornado_battery.mysql import option_name

    assert option_name('master', 'uri') == 'mysql-master-uri'
    assert option_name('slave', 'uri') == 'mysql-slave-uri'
