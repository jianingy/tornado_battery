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
from tornado_battery.redis import register_redis_options, with_redis
from tornado_battery.redis import RedisConnector, RedisConnectorError
import pytest

pytestmark = pytest.mark.asyncio
register_redis_options('test', 'redis://127.0.0.1/0')


@pytest.fixture
async def redis():
    from tornado_battery.redis import connect_redis
    redis = RedisConnector.instance('test')
    connect = connect_redis('test')
    await connect()
    return redis


@pytest.mark.asyncio
async def test_set_command(redis):
    db = await redis.acquire()
    value = await db.execute('set', 'redis_value', '1984')
    redis.release()
    assert value == 'OK'


@pytest.mark.asyncio
async def test_get_command(redis):
    db = await redis.acquire()
    await db.execute('set', 'redis_value', '1984')
    value = await db.execute('get', 'redis_value')
    redis.release()
    assert value == '1984'


@pytest.mark.asyncio
async def test_decorator(redis):

    @with_redis(name='test')
    async def _read(redis):
        value = await redis.execute('set', 'redis_decorator_value', '1983')
        return value
    assert (await _read()) == 'OK'


@pytest.mark.asyncio
async def test_decorator_duplicated(redis):

    @with_redis(name='test')
    async def _read(redis):
        value = await redis.execute('set', 'redis_decorator_value', '1983')
        return value
    with pytest.raises(RedisConnectorError):
        await _read(redis=None)


@pytest.mark.asyncio
async def test_no_connection_to_release():
    match = r'^no connection of norel to release$'
    with pytest.raises(RedisConnectorError, match=match):
        RedisConnector.instance('norel').release()


@pytest.mark.asyncio
async def test_not_connect():
    match = r'^no connection of noconn found$'
    with pytest.raises(RedisConnectorError, match=match):
        await RedisConnector.instance('noconn').acquire()


@pytest.mark.asyncio
async def test_invalid_connection_scheme():
    from tornado.options import options
    options.redis_test_uri = 'test://'
    match = r' is not a redis connection scheme$'
    with pytest.raises(RedisConnectorError, match=match):
        await RedisConnector.instance('test').connect()


@pytest.mark.asyncio
async def test_option_name():
    from tornado_battery.redis import option_name

    assert option_name('master', 'uri') == 'redis-master-uri'
    assert option_name('slave', 'uri') == 'redis-slave-uri'
