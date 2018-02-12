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

    def setup_options(self):
        name = self.name
        opts = options.group_dict('%s database' % name)
        uri = opts[option_name(name, "uri")]
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
        self._reconnect_interval = opts[option_name(name, "reconnect-interval")]
        self._num_connections = opts[option_name(name, "num-connections")]

    async def connection(self):
        if not hasattr(self, '_connections') or not self._connections:
            await self.connect()
        new = await self._connections.getconn()
        return self._connections.manage(new)

    async def connect(self):
        self.setup_options()
        LOG.info('connecting postgresql %s' % self._connection_string)
        self._connections = momoko.Pool(
            dsn=self._connection_string,
            reconnect_interval=self._reconnect_interval,
            size=int(self._num_connections[0]),
            max_size=int(self._num_connections[-1]),
            ioloop=tornado.ioloop.IOLoop.instance(),
        )
        await self._connections.connect()


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
    define(option_name(instance, 'num-connections'), multiple=True,
           default=[1, 2],
           group='%s database' % instance,
           help='connection pool size for %s ' % instance)
    define(option_name(instance, 'reconnect-interval'),
           default=5,
           group='%s database' % instance,
           help='reconnect interval for %s' % instance)
