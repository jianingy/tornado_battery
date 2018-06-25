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

import asyncio
import functools
import logging
from cassandra.cluster import Cluster
from cassandra.policies import RoundRobinPolicy
from aiocassandra import aiosession


LOG = logging.getLogger('tornado.application')


class CassandraConnectorError(ServerException):
    pass


class CassandraConnector(NamedSingletonMixin):

    def __init__(self, name: str):  # NOQA
        self.name = name

    def connection(self):
        if not hasattr(self, '_session') or not self._session:
            raise CassandraConnectorError(
                "no session of %s found" % self.name)
        return self._session

    async def connect(self, load_balancing_policy=None):
        name = self.name
        opts = options.group_dict('%s cassandra' % name)
        points = opts[option_name(name, 'points')]
        contact_points = points.split(',')
        port = opts[option_name(name, 'port')]
        executor_threads = opts[option_name(name, 'executor-threads')]
        _load_balancing_policy = load_balancing_policy or RoundRobinPolicy()
        LOG.info('connecting cassandra [%s] %s' % (self.name, points))

        # TODO 选取合适的loadbalancingpolicy
        # Cluster.__init__ called with contact_points specified
        # should specify a load-balancing policy
        # http://datastax.github.io/python-driver/_modules/cassandra/cluster.html#Cluster # NOQA
        # RoundRobinPolicy:
        # http://datastax.github.io/python-driver/_modules/cassandra/policies.html#RoundRobinPolicy # NOQA
        cluster = Cluster(contact_points=contact_points,
                          port=port, executor_threads=executor_threads,
                          load_balancing_policy=_load_balancing_policy)
        self._session = cluster.connect()
        aiosession(self._session)


def option_name(instance: str, option: str) -> str:
    return 'cassandra-%s-%s' % (instance, option)


def register_cassandra_options(instance: str='default',
                               points: str='127.0.0.1',
                               port: int=9042,
                               executor_threads: int=2):
    define(option_name(instance, "points"),
           default=points,
           group='%s cassandra' % instance,
           help='cassandra contact points for %s' % instance)
    define(option_name(instance, 'port'),
           default=port,
           group='%s cassandra' % instance,
           help='cassandra port for %s ' % instance)
    define(option_name(instance, 'executor-threads'),
           default=executor_threads,
           group='%s cassandra' % instance,
           help='num of cassandra executor_threads for %s ' % instance)


def with_cassandra(name: str):

    def wrapper(function):

        @functools.wraps(function)
        async def f(*args, **kwargs):
            cassandra = CassandraConnector.instance(name).connection()
            if 'cassandra' in kwargs:
                raise CassandraConnectorError(
                    'duplicated argument for cassandra %s' % name)
            kwargs.update({'cassandra': cassandra})
            retval = await function(*args, **kwargs)
            return retval
        return f

    return wrapper


def connect_cassandra(name: str):
    return CassandraConnector.instance(name).connect
