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


class MysqlConnectorError(ServerException):
    pass


class MysqlConnector(NamedSingletonMixin):

    def __init__(self, name: str):
        self.name = name

    def connection(self):
        if not hasattr(self, '_connections') or not self._connections:
            raise MysqlConnectorError("no connection of %s found" % self.name)
        return self._connections.acquire()

    def setup_options(self):
        name = self.name
        opts = options.group_dict('%s database' % name)
        uri = opts[option_name(name, "uri")]
        r = urlparse(uri)
        if r.scheme.lower() != 'mysql':
            raise MysqlConnectorError('%s is not a mysql connection scheme' % uri)
        self._host = r.hostname or 'localhost'
        self._port = r.port or 3306
        self._user = r.username
        self._password = r.password
        self._db = r.path.lstrip('/') or r.username
        fmt = ('host={host} port={port} dbname={db} user={user} password={pw}')
        dsn = fmt.format(host=self._host,
                         port=self._port,
                         user=self._user,
                         pw=self._password,
                         db=self._db)
        self._connection_string = dsn
        self._num_connections = opts[option_name(name, "num-connections")]
        self._pool_recycle = opts[option_name(name, "pool-recycle")]

    async def connect(self, event_loop=None):
        self.setup_options()
        LOG.info('connecting mysql [%s] %s' %
                 (self.name, self._connection_string))
        if event_loop is None:
            event_loop = asyncio.get_event_loop()
        self._connections = await aiomysql.create_pool(
            host=self._host,
            port=self._port,
            user=self._user,
            password=self._password,
            db=self._db,
            minsize=int(self._num_connections[0]),
            maxsize=int(self._num_connections[-1]),
            autocommit=True,
            pool_recycle=self._pool_recycle,
            loop=event_loop, charset="utf8"
        )
        return self._connections


def option_name(instance: str, option: str) -> str:
    return 'mysql-%s-%s' % (instance, option)


def register_mysql_options(instance: str='master', default_uri: str='mysql:///'):
    define(option_name(instance, "uri"),
           default=default_uri,
           group='%s database' % instance,
           help="mysql connection uri for %s" % instance)
    define(option_name(instance, 'num-connections'), multiple=True,
           default=[1, 4],
           group='%s database' % instance,
           help='connection pool size for %s ' % instance)
    define(option_name(instance, 'pool-recycle'),
           default=30,
           group='%s database' % instance,
           help='pool recycle timeout for %s' % instance)


def with_mysql(name: str):

    def wrapper(function):

        @functools.wraps(function)
        async def f(*args, **kwargs):
            async with MysqlConnector.instance(name).connection() as db:
                LOG.debug("mysql connection acquired.")
                if "db" in kwargs:
                    raise MysqlConnectorError(
                        "duplicated database argument for database %s" % name)
                kwargs.update({"db": db})
                retval = await function(*args, **kwargs)
                return retval
        return f

    return wrapper


def connect_mysql(name: str):
    return MysqlConnector.instance(name).connect
