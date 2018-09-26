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
import time
from tornado_battery.cassandra import (
    register_cassandra_options, with_cassandra, connect_cassandra)
from tornado_battery.cassandra import (
    CassandraConnector, CassandraConnectorError)
import pytest

pytestmark = pytest.mark.asyncio
register_cassandra_options(
    'test',
    default_uri='cassandra://cassandra:cassandra@127.0.0.1:9042/system'
    '?charset=utf8')


@pytest.fixture
async def cassandra():
    cassandra = CassandraConnector.instance('test')
    connect = connect_cassandra('test')
    await connect()
    session = cassandra.connection()
    cql_keyspace_create = """
        CREATE KEYSPACE IF NOT EXISTS testtmp WITH
        replication = {'class': 'SimpleStrategy',
        'replication_factor' : 1}
    """
    q = await session.prepare_future(cql_keyspace_create)
    await session.execute_future(q)
    q = await session.prepare_future('USE testtmp')
    await session.execute_future(q)
    cql_tb_create = ('CREATE TABLE tmp_tornado_battery_test ('
                     'specid text PRIMARY KEY,'
                     'foo text,'
                     'bar int'
                     ')')
    cql_tb_drop = 'DROP TABLE IF EXISTS tmp_tornado_battery_test'
    q = await session.prepare_future(cql_tb_drop)
    await session.execute_future(q)
    q = await session.prepare_future(cql_tb_create)
    await session.execute_future(q)
    return cassandra


async def test_cql(cassandra):
    now = int(time.time())
    cql = """
        INSERT INTO tmp_tornado_battery_test (specid, foo, bar)
        VALUES ('test', 'foo0', ?)
    """
    session = cassandra.connection()
    query = await session.prepare_future(cql)
    await session.execute_future(query, (now, ))
    cql = """
        SELECT foo, bar FROM tmp_tornado_battery_test WHERE specid='test';
    """
    query = await session.prepare_future(cql)
    values = await session.execute_future(query)
    assert(values[0][0] == 'foo0')
    assert(values[0][1] == now)


async def test_decorator(cassandra):
    now = int(time.time())

    @with_cassandra(name='test')
    async def _read(now, cassandra=None):
        cql = """
            INSERT INTO tmp_tornado_battery_test (specid, foo, bar)
            VALUES ('test', 'foo0', ?)
        """
        query = await cassandra.prepare_future(cql)
        await cassandra.execute_future(query, (now, ))
        cql = """
            SELECT foo, bar FROM tmp_tornado_battery_test WHERE specid='test';
        """
        query = await cassandra.prepare_future(cql)
        values = await cassandra.execute_future(query)
        return values
    values = await _read(now)
    assert(values[0][0] == 'foo0')
    assert(values[0][1] == now)


async def test_decorator_duplicated(cassandra):

    @with_cassandra(name='test')
    async def _read(cassandra):
        cql = """
            SELECT foo, bar FROM tmp_tornado_battery_test WHERE specid='test';
        """
        query = await cassandra.prepare_future(cql)
        values = await cassandra.execute_future(query)
        return values

    with pytest.raises(CassandraConnectorError):
        await _read(cassandra=None)


async def test_invalid_connection_scheme():
    from tornado.options import options
    options.cassandra_test_uri = 'test://'
    match = r' is not a cassandra connection scheme$'
    with pytest.raises(CassandraConnectorError, match=match):
        await CassandraConnector.instance('test').connect()


async def test_option_name():
    from tornado_battery.cassandra import option_name

    assert option_name('test', 'points') == 'cassandra-test-points'


async def test_no_session_connector():
    with pytest.raises(CassandraConnectorError):
        CassandraConnector.instance('nosession').connection()
