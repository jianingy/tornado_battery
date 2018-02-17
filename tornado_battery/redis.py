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
from .exception import GeneralException
from .pattern import NamedSingletonMixin
from tornado.options import define, options
from urllib.parse import urlparse

import aioredis
import logging

LOG = logging.getLogger('tornado.application')


class RedisConnectorError(GeneralException):
    pass


class RedisConnector(NamedSingletonMixin):

    def __init__(self, name):
        self.name = name

    def connection(self):
        if not hasattr(self, '_connections') or not self._connections:
            raise RedisConnectorError("no connection found")
        return self._connections.get()

    async def connect(self):
        name = self.name
        opts = options.group_dict('%s redis' % name)
        connection_string = opts[option_name(name, "uri")]
        r = urlparse(connection_string)
        if r.scheme.lower() != 'redis':
            raise RedisConnector('%s is not a redis connection scheme' % connection_string)
        num_connections = opts[option_name(name, "num-connections")]
        LOG.info('connecting redis %s' % connection_string)
        self._connections = await aioredis.create_pool(
            connection_string,
            encoding="UTF-8",
            minsize=int(num_connections[0]),
            maxsize=int(num_connections[-1])
        )


def option_name(instance, option):
    if instance == 'master':
        return 'redis-%s' % option
    else:
        return 'redis-%s-%s' % (instance, option)


def register_redis_options(instance='master', default_uri='redis:///'):
    define(option_name(instance, "uri"),
           default=default_uri,
           group='%s redis' % instance,
           help="redis connection uri for %s" % instance)
    define(option_name(instance, 'num-connections'), multiple=True,
           default=[1, 2],
           group='%s redis' % instance,
           help='# of redis connections for %s ' % instance)
