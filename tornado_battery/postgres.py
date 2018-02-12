# -*- coding: utf-8 -*-
#
# This piece of code is written by
#    Jianing Yang <jianingy.yang@gmail.com>
# with love and passion!
#
#        H A P P Y    H A C K I N G !
#              _____               ______
#     ____====  ]OO|_n_n__][.      |    |
#    [________]_|__|________)<     |YANG|
#     oo    oo  'oo OOOO-| oo\\_   ~o~~~o~
# +--+--+--+--+--+--+--+--+--+--+--+--+--+
#                             22 Jan, 2016
#
from .exception import GeneralException
from tornado.options import define, options
from urllib.parse import urlparse

import logging
import momoko
import platform
import threading
import tornado.ioloop
if platform.python_implementation() == 'PyPy':
    import psycopg2cffi.compat  # noqa
    psycopg2cffi.compat.register()
else:
    import psycopg2             # noqa

LOG = logging.getLogger('tornado.application')


class PostgresConnectorError(GeneralException):
    pass


class PostgresConnector:

    __instance_lock = threading.Lock()
    __instances = dict()

    @classmethod
    def instance(cls, name='master'):
        if name not in cls.__instances:
            with cls.__instance_lock:
                LOG.debug("create a new postgres instance for '%s'" % name)
                PostgresConnector.__instances[name] = PostgresConnector(name)
        return PostgresConnector.__instances[name]

    def __init__(self, name):
        self.name = name

    def setup(self, uri, **kwargs):
        r = urlparse(uri)
        if r.scheme.lower() != 'postgres':
            raise PostgresConnectorError('%s is not a postgres connection scheme' % uri)
        fmt = ('host={host} port={port} dbname={db} user={user} password={pw}')
        dsn = fmt.format(host=r.hostname or 'localhost',
                         port=r.port or 5432,
                         user=r.username,
                         pw=r.password,
                         db=r.path.lstrip('/') or r.username)
        self._connection_string = dsn
        self._reconnect_interval = kwargs.get('reconnect_interval', 5)
        self._pool_size = kwargs.get('max_pool_size', 4)

    async def connection(self):
        if not hasattr(self, '_connections') or not self._connections:
            await self.connect()
        return self._connections

    async def connect(self):
        name = self.name
        opts = options.group_dict('%s database' % name)
        connection_string = opts[option_name(name, "uri")]
        LOG.info('connecting postgresql %s' % connection_string)
        self._connections = momoko.Pool(
            dsn=connection_string,
            reconnect_interval=opts[option_name(name, "reconnect-interval")],
            size=opts[option_name(name, "max-pool-size")],
            ioloop=tornado.ioloop.IOLoop.instance(),
        )
        await self._connections.connect()

    def disconnect(self):
        self._connections.close()
        delattr(self._connections)


def option_name(instance, option):
    if instance == 'master':
        return 'postgres-%s' % option
    else:
        return 'postgres-%s-%s' % (instance, option)


def register_postgres_options(instance='master', default_uri='postgres:///'):
    define(option_name(instance, "uri"),
           default=default_uri,
           group='%s database' % instance,
           help="postgresql connection uri for %s" % instance)
    define(option_name(instance, 'max-pool-size'),
           default=4,
           group='%s database' % instance,
           help='connection pool size for %s ' % instance)
    define(option_name(instance, 'reconnect-interval'),
           default=5,
           group='%s database' % instance,
           help='reconnect interval for %s' % instance)
