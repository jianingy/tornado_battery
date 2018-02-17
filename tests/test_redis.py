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
from tornado_battery.redis import RedisConnector
import pytest

pytestmark = pytest.mark.asyncio
register_redis_options("test", "redis://127.0.0.1/0")


@pytest.fixture
async def redis():
    redis = RedisConnector.instance("test")
    await redis.connect()
    return redis


async def test_set_command(redis):
    async with redis.connection() as db:
        value = await db.execute("set", "redis_value", "1984")
    assert value == "OK"


async def test_get_command(redis):
    async with redis.connection() as db:
        await db.execute("set", "redis_value", "1984")
        value = await db.execute("get", "redis_value")
    assert value == "1984"


async def test_decorator(redis):

    @with_redis(name="test")
    async def _read(redis):
        value = await redis.execute("set", "redis_decorator_value", "1983")
        return value
    assert (await _read()) == "OK"
