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
from asyncio import wait as async_wait
from tornado_battery.redis import register_redis_options, with_redis
from tornado_battery.redis import RedisConnector
from tornado_battery.locks import throttle, ThrottleExceeded
import pytest

pytestmark = pytest.mark.asyncio
register_redis_options('locks', 'redis://127.0.0.1/0')


@pytest.fixture
async def redis():
    redis = RedisConnector.instance('locks')
    await redis.connect()
    yield redis


@with_redis(name='locks')
async def clear(key, redis):
    await redis.execute('DEL', f'throttle_{key}')


@with_redis(name='locks')
async def get_lock_value(key, redis):
    value = await redis.execute('GET', f'throttle_{key}')
    return value


async def test_throttle_serial(redis):

    @with_redis(name='locks')
    async def _read(redis):
        async with throttle(redis, 'TEST_LOCK_1', 2, 5) as value:
            return value

    await clear('TEST_LOCK_1')
    value = await _read()
    value = await _read()
    assert value == 2


async def test_throttle_concurrent(redis):

    @with_redis(name='locks')
    async def _read(redis):
        async with throttle(redis, 'TEST_LOCK_2', 2, 5) as value:
            return value

    await clear('TEST_LOCK_2')
    tasks, _ = await async_wait([_read(), _read()])
    list(map(lambda x: x.result(), tasks))


async def test_throttle_exceeded(redis):

    @with_redis(name='locks')
    async def _read(redis):
        async with throttle(redis, 'TEST_LOCK_3', 1, 5) as value:
            return value

    await clear('TEST_LOCK_3')
    with pytest.raises(ThrottleExceeded):
        tasks, _ = await async_wait([_read(), _read()])
        list(map(lambda x: x.result(), tasks))


async def test_throttle_with_release_serial(redis):

    @with_redis(name='locks')
    async def _read(redis):
        async with throttle(redis, 'TEST_LOCK_4', 1, 5, release=True) as value:
            return value

    await clear('TEST_LOCK_4')
    value = await _read()
    value = await _read()
    assert value == 1


async def test_throttle_with_release_concurrent(redis):

    @with_redis(name='locks')
    async def _read(redis):
        async with throttle(redis, 'TEST_LOCK_5', 1, 5, release=True) as value:
            return value

    await clear('TEST_LOCK_5')
    tasks, _ = await async_wait([_read(), _read()])
    list(map(lambda x: x.result(), tasks))


async def test_throttle_with_release_by_exception(redis):

    @with_redis(name='locks')
    async def _read(redis):
        async with throttle(redis, 'TEST_LOCK_6', 1, 5, release=True) as value:
            assert (await get_lock_value('TEST_LOCK_6')) == '1'
            raise RuntimeError('runtime error')
            return value

    await clear('TEST_LOCK_6')
    with pytest.raises(RuntimeError):
        await _read()
    assert (await get_lock_value('TEST_LOCK_6')) == '0'
