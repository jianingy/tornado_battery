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
"""
A set of utilities which leveraging redis to do synchronization easily
for common business logic.
"""
from asyncio_extras import async_contextmanager
import logging


LOG = logging.getLogger('tornado.application')


class ThrottleExceeded(Exception):

    def __init__(self, name, amount):
        self.name = name
        self.amount = amount


@async_contextmanager
async def throttle(redis, name, amount, expire=None, release=False):
    """
    Example:

    A constraint prevent any user from bidding more than 15
    times every 600 seconds.

    Code:

        async with throttle(redis, 'BIDS_%s' % user_id, 15, 600) as value:
            # doing something

    Notes:

        The value of the throttle will be increased every time
        entering the context and decreased every time leaving
        the context. NOTICE, any exception inside the context
        will cause the throttle decreased.

    """
    redis_key = f'throttle_{name}'
    value = await redis.execute('INCR', redis_key)
    if expire:
        await redis.expire(redis_key, expire)
    if value <= amount:
        try:
            yield value
            if release:
                await redis.execute('DECR', redis_key)
        except Exception as e:
            LOG.warn('throttle %s decreased due to exception', name)
            await redis.execute('DECR', redis_key)
            raise e
    else:
        LOG.info('throttle %s exceeded %s', name, amount)
        await redis.execute('DECR', redis_key)
        raise ThrottleExceeded(name, amount)
