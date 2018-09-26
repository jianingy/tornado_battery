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
from aiocassandra import aiosession
from cassandra.auth import PlainTextAuthProvider
from cassandra.cluster import Cluster
from cassandra.policies import RoundRobinPolicy
from tornado.options import define, options
from urllib.parse import urlparse

import functools
import logging

from .exception import ServerException
from .pattern import NamedSingletonMixin


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


class CassandraConnectorError(ServerException):
    error_code = 600101


class CassandraConnector(NamedSingletonMixin):

    def __init__(self, name: str):  # NOQA
        self.name = name

    def connection(self):
        if not hasattr(self, '_session') or not self._session:
            raise CassandraConnectorError(f'no session of {self.name} found')
        return self._session

    async def connect(self, load_balancing_policy=None):
        name = self.name
        opts = options.group_dict(f'{name} cassandra')
        uri = opts[option_name(name, 'uri')]
        r = urlparse(uri)
        query_as_dict(r.query)
        if r.scheme.lower() != 'cassandra':
            raise CassandraConnectorError(
                f'{uri} is not a cassandra connection scheme')
        self._hosts = r.hostname.split(',') if r.hostname else ['127.0.0.1']
        self._port = r.port or 9042
        self._keyspace = None
        self._user = r.username
        self._password = r.password
        keyspace = r.path.lstrip('/')
        if keyspace:
            self._keyspace = keyspace
        executor_threads = opts[option_name(name, 'executor-threads')]
        _load_balancing_policy = load_balancing_policy or RoundRobinPolicy()
        LOG.info(f'connecting cassandra [{self.name}] {uri}')
        auth_provider = PlainTextAuthProvider(
            username=self._user, password=self._password)

        # TODO 选取合适的loadbalancingpolicy
        # Cluster.__init__ called with contact_points specified
        # should specify a load-balancing policy
        # http://datastax.github.io/python-driver/_modules/cassandra/cluster.html#Cluster # NOQA
        # RoundRobinPolicy:
        # http://datastax.github.io/python-driver/_modules/cassandra/policies.html#RoundRobinPolicy # NOQA
        cluster = Cluster(contact_points=self._hosts,
                          port=self._port, executor_threads=executor_threads,
                          load_balancing_policy=_load_balancing_policy,
                          auth_provider=auth_provider)
        self._session = cluster.connect(keyspace=self._keyspace)
        aiosession(self._session)


def option_name(instance: str, option: str) -> str:
    return f'cassandra-{instance}-{option}'


def register_cassandra_options(
        instance: str='default',
        default_uri: str='cassandra:///',
        executor_threads: int=2):
    define(option_name(instance, 'uri'),
           default=default_uri,
           group=f'{instance} cassandra',
           help=f'cassandra contact uri {instance}')
    define(option_name(instance, 'executor-threads'),
           default=executor_threads,
           group=f'{instance} cassandra',
           help=f'num of cassandra executor_threads for {instance}')


def with_cassandra(name: str):

    def wrapper(function):

        @functools.wraps(function)
        async def f(*args, **kwargs):
            cassandra = CassandraConnector.instance(name).connection()
            if 'cassandra' in kwargs:
                raise CassandraConnectorError(
                    f'duplicated argument for cassandra {name}')
            kwargs.update({'cassandra': cassandra})
            retval = await function(*args, **kwargs)
            return retval
        return f

    return wrapper


def connect_cassandra(name: str):
    return CassandraConnector.instance(name).connect
