# -*- coding: utf-8 -*-

from .exception import ServerException
from .pattern import NamedSingletonMixin
from tornado.options import define, options
from urllib.parse import urlparse

import asyncio
import aiomysql
import functools
import logging

LOG = logging.getLogger('tornado.application')


def query_as_dict(query: str) -> dict:
    result = dict()
    if not query:
        return result
    item_list = query.split('&')
    for item in item_list:
        key, value = item.split('=')
        result[key] = value
    return result


class MysqlConnectorError(ServerException):
    pass


class MysqlConnector(NamedSingletonMixin):

    def __init__(self, name: str):
        self.name = name

    def connection(self):
        if not hasattr(self, '_connections') or not self._connections:
            raise MysqlConnectorError(f'no connection of {self.name} found')
        return self._connections.acquire()

    def setup_options(self):
        name = self.name
        opts = options.group_dict(f'{name} database')
        uri = opts[option_name(name, 'uri')]
        r = urlparse(uri)
        q = query_as_dict(r.query)
        if r.scheme.lower() != 'mysql':
            raise MysqlConnectorError(
                f'{uri} is not a mysql connection scheme')
        self._host = r.hostname or 'localhost'
        self._port = r.port or 3306
        self._user = r.username
        self._password = r.password
        self._db = r.path.lstrip('/') or r.username
        self._charset = q.get('charset') or 'utf8mb4'
        fmt = ('host={host} port={port} dbname={db} '
               'user={user} password={pw} charset={charset}')
        dsn = fmt.format(host=self._host,
                         port=self._port,
                         user=self._user,
                         pw=self._password,
                         db=self._db,
                         charset=self._charset)
        self._connection_string = dsn
        self._num_connections = opts[option_name(name, 'num-connections')]
        self._pool_recycle = opts[option_name(name, 'pool-recycle')]

    async def connect(self, autocommit=True, event_loop=None):
        self.setup_options()
        LOG.info(f'connecting mysql [{self.name}] {self._connection_string}')
        if event_loop is None:
            event_loop = asyncio.get_event_loop()
        self._connections = await aiomysql.create_pool(
            host=self._host,
            port=self._port,
            user=self._user,
            password=self._password,
            db=self._db,
            charset=self._charset,
            minsize=int(self._num_connections[0]),
            maxsize=int(self._num_connections[-1]),
            autocommit=autocommit,
            pool_recycle=self._pool_recycle,
            loop=event_loop,
        )
        return self._connections


def option_name(instance: str, option: str) -> str:
    return f'mysql-{instance}-{option}'


def register_mysql_options(instance: str='master',
                           default_uri: str='mysql://'):
    define(option_name(instance, 'uri'),
           default=default_uri,
           group=f'{instance} database',
           help=f'mysql connection uri for {instance}')
    define(option_name(instance, 'num-connections'), multiple=True,
           default=[1, 4],
           group=f'{instance} database',
           help=f'connection pool size for {instance}')
    define(option_name(instance, 'pool-recycle'),
           default=30,
           group=f'{instance} database',
           help=f'pool recycle timeout for {instance}')


def with_mysql(name: str):

    def wrapper(function):

        @functools.wraps(function)
        async def f(*args, **kwargs):
            async with MysqlConnector.instance(name).connection() as db:
                LOG.debug('mysql connection acquired.')
                if 'db' in kwargs:
                    raise MysqlConnectorError(
                        f'duplicated database argument for database {name}')
                kwargs.update({'db': db})
                retval = await function(*args, **kwargs)
                return retval
        return f

    return wrapper


def connect_mysql(name: str, autocommit: bool=True):
    async def _connect(event_loop=None):
        return await MysqlConnector.instance(name).connect(autocommit,
                                                           event_loop)
    return _connect
