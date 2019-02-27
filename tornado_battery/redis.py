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
from tornado.ioloop import IOLoop
from urllib.parse import urlparse

import aioredis
import asyncio
import functools
import logging
import peewee_async

LOG = logging.getLogger('tornado.application')


class RedisConnectorError(ServerException):
    error_code = 500010


class RedisConnector(NamedSingletonMixin):

    def __init__(self, name: str):
        self.name = name
        self.task_locals = peewee_async.TaskLocals(loop=None)

    async def acquire(self):
        if not hasattr(self, '_connections') or not self._connections:
            raise RedisConnectorError(f'no connection of {self.name} found')
        connection = self.task_locals.get('acquired_connection', None)
        if connection:
            count = self.task_locals.get('acquired_count', 0)
            self.task_locals.set('acquired_count', count + 1)
            LOG.debug(f'acquired previous connection of {self.name} '
                      f'{id(connection)} ({count + 1})')
        else:
            connection = await self._connections.acquire()
            LOG.debug(f'acquired new connection of {self.name} '
                      f'{id(connection)}(1)')
            self.task_locals.set('acquired_count', 1)
            self.task_locals.set('acquired_connection', connection)
        return connection

    def release(self):
        count = self.task_locals.get('acquired_count', 0) - 1
        if count < 0:
            raise RedisConnectorError(f'no connection of {self.name}'
                                      ' to release')
        self.task_locals.set('acquired_count', count)
        if count > 0:
            return
        connection = self.task_locals.get('acquired_connection', None)
        LOG.debug(f'release connection {id(connection)}')
        self._connections.release(connection)

        self.task_locals.set('acquired_connection', None)

    async def connect(self, event_loop=None):
        name = self.name
        opts = options.group_dict(f'{name} redis')
        connection_string = opts[option_name(name, 'uri')]
        r = urlparse(connection_string)
        if r.scheme.lower() != 'redis':
            raise RedisConnectorError(
                f'{connection_string} is not a redis connection scheme')
        num_connections = opts[option_name(name, 'num-connections')]
        LOG.debug(f'connecting redis [{self.name}] {connection_string}')
        if event_loop is None:
            event_loop = asyncio.get_event_loop()
        self._connections = await aioredis.create_pool(
            connection_string,
            encoding='UTF-8',
            minsize=int(num_connections[0]),
            maxsize=int(num_connections[-1]),
            loop=event_loop,
        )


def option_name(instance: str, option: str) -> str:
    return f'redis-{instance}-{option}'


def register_redis_options(instance: str = 'master',
                           default_uri: str = 'redis://'):
    define(option_name(instance, 'uri'),
           default=default_uri,
           group=f'{instance} redis',
           help=f'redis connection uri for {instance}')
    define(option_name(instance, 'num-connections'), multiple=True,
           default=[1, 2],
           group=f'{instance} redis',
           help=f'# of redis connections for {instance}')


def with_redis(name: str):

    def wrapper(function):

        @functools.wraps(function)
        async def f(*args, **kwargs):
            if 'redis' in kwargs:
                raise RedisConnectorError(
                    f'duplicated database argument for redis {name}')
            connector = RedisConnector.instance(name)
            connection = await connector.acquire()
            redis = aioredis.Redis(connection)
            kwargs.update({'redis': redis})
            try:
                retval = await function(*args, **kwargs)
                return retval
            finally:
                connector.release()
        return f

    return wrapper


def connect_redis(name: str):
    return RedisConnector.instance(name).connect
