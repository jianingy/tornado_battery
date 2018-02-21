# -*- coding: utf-8 -*-
#
#        H A P P Y    H A C K I N G !
#              _____               ______
#     ____====  ]OO|_n_n__][.      |    |
#    [________]_|__|________)<     |YANG|
#     oo    oo  'oo OOOO-| oo\\_   ~o~~o~
# +--+--+--+--+--+--+--+--+--+--+--+--+--+
#               Jianing Yang @ 12 Feb, 2018
#
from .exception import ServerException
from .pattern import NamedSingletonMixin
from tornado.options import define, options
from urllib.parse import urlparse

import aioredis
import asyncio
import functools
import logging

LOG = logging.getLogger('tornado.application')


class RedisConnectorError(ServerException):
    pass


class RedisConnector(NamedSingletonMixin):

    def __init__(self, name: str):
        self.name = name

    def connection(self):
        if not hasattr(self, '_connections') or not self._connections:
            raise RedisConnectorError("no connection of %s found" % self.name)
        return self._connections.get()

    async def connect(self, event_loop=None):
        name = self.name
        opts = options.group_dict('%s redis' % name)
        connection_string = opts[option_name(name, "uri")]
        r = urlparse(connection_string)
        if r.scheme.lower() != 'redis':
            raise RedisConnectorError('%s is not a redis connection scheme' %
                                      connection_string)
        num_connections = opts[option_name(name, "num-connections")]
        LOG.info('connecting redis [%s] %s' % (self.name, connection_string))
        if event_loop is None:
            event_loop = asyncio.get_event_loop()
        self._connections = await aioredis.create_pool(
            connection_string,
            encoding="UTF-8",
            minsize=int(num_connections[0]),
            maxsize=int(num_connections[-1]),
            loop=event_loop
        )


def option_name(instance: str, option: str) -> str:
    return 'redis-%s-%s' % (instance, option)


def register_redis_options(instance: str='master', default_uri: str='redis:///'):
    define(option_name(instance, "uri"),
           default=default_uri,
           group='%s redis' % instance,
           help="redis connection uri for %s" % instance)
    define(option_name(instance, 'num-connections'), multiple=True,
           default=[1, 2],
           group='%s redis' % instance,
           help='# of redis connections for %s ' % instance)


def with_redis(name: str):

    def wrapper(function):

        @functools.wraps(function)
        async def f(*args, **kwargs):
            async with RedisConnector.instance(name).connection() as redis:
                if "redis" in kwargs:
                    raise RedisConnectorError(
                        "duplicated database argument for redis %s" % name)
                kwargs.update({"redis": aioredis.Redis(redis)})
                retval = await function(*args, **kwargs)
                return retval
        return f

    return wrapper


def connect_redis(name: str):
    return RedisConnector.instance(name).connect
