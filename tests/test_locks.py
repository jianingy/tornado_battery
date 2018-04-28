# -*- coding: utf-8 -*-
#
#        H A P P Y    H A C K I N G !
#              _____               ______
#     ____====  ]OO|_n_n__][.      |    |
#    [________]_|__|________)<     |YANG|
#     oo    oo  'oo OOOO-| oo\\_   ~o~~o~
# +--+--+--+--+--+--+--+--+--+--+--+--+--+
#               Jianing Yang @ 28 Apr, 2018
#
from tornado_battery.redis import register_redis_options, with_redis
from tornado_battery.redis import RedisConnector, RedisConnectorError
from tornado_battery.locks import throttle
import pytest

pytestmark = pytest.mark.asyncio
register_redis_options("test", "redis://127.0.0.1/0")


@pytest.fixture
async def redis():
    redis = RedisConnector.instance("test")
    await redis.connect()
    return redis


async def test_decorator(redis):

    @with_redis(name="test")
    async def _read(redis):
        async with throttle(redis, "LOCK_1", 1, 5) as value:
            raise NotImplemented()

    raise NotImplemented()


async def test_decorator_duplicated(redis):

    @with_redis(name="test")
    async def _read(redis):
        value = await redis.execute("set", "redis_decorator_value", "1983")
        return value
    with pytest.raises(RedisConnectorError):
        await _read(redis=None)


async def test_no_connection():
    match = r"^no connection of noconn found$"
    with pytest.raises(RedisConnectorError, match=match):
        RedisConnector.instance("noconn").connection()


async def test_invalid_connection_scheme():
    from tornado.options import options
    options.redis_test_uri = "test://"
    match = r" is not a redis connection scheme$"
    with pytest.raises(RedisConnectorError, match=match):
        await RedisConnector.instance("test").connect()


async def test_option_name():
    from tornado_battery.redis import option_name

    assert option_name("master", "uri") == "redis-master-uri"
    assert option_name("slave", "uri") == "redis-slave-uri"
