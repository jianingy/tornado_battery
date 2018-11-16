# -*- coding: UTF-8 -*-
from contextlib import contextmanager
from playhouse.db_url import connect as db_connect
from tornado_battery.pattern import SingletonMixin
from urllib.parse import urlparse

import functools
import logging
import peewee
import peewee_async


LOG = logging.getLogger('tornado.application')


class Replications(SingletonMixin):
    __slots__ = ('obj', '_connections', '_callbacks')

    def __init__(self):
        self._connections = {}

    @staticmethod
    def _connection_string(uri):
        parsed = urlparse(uri)
        if parsed.scheme.lower() in ('postgres', 'postgresql'):
            replaced = parsed._replace(scheme='postgres+pool+async')
            return replaced.geturl()
        raise NotImplementedError('only support postgresql')

    def add(self, name, uri, allow_sync=False):
        LOG.info(f'{name} database {uri} initialized')
        conn = db_connect(Replications._connection_string(uri))
        conn.set_allow_sync(allow_sync)
        self._connections[name] = conn

    @property
    def names(self):
        return self._connections.keys()

    def connection(self, name):
        return self._connections[name]


class ReplicationManager(SingletonMixin):

    local_key = 'tornado_battery.orm.manager'

    def __init__(self):
        self._mgmt = {}
        self.initialize()
        self.task_locals = peewee_async.TaskLocals(loop=None)

    def initialize(self):
        repl = Replications.instance()

        for name in repl.names:
            conn = repl.connection(name)
            self._mgmt[name] = peewee_async.Manager(conn)

    @contextmanager
    def use(self, name):
        assert name in self._mgmt
        mgmt_stack = self.task_locals.get(self.local_key, None)
        if mgmt_stack is None:
            mgmt_stack = []
            self.task_locals.set(self.local_key, mgmt_stack)
        mgmt_stack.append(self._mgmt[name])
        try:
            yield self._mgmt[name]
        finally:
            mgmt_stack.pop()

    def get(self):
        mgmt_stack = self.task_locals.get(self.local_key, None)
        assert mgmt_stack is not None, 'no orm manager is in use'
        return mgmt_stack[-1]


def use_orm(name: str):

    def wrapper(function):

        @functools.wraps(function)
        async def f(*args, **kwargs):
            with ReplicationManager.instance().use(name):
                retval = await function(*args, **kwargs)
            return retval
        return f

    return wrapper


def with_orm(function):

    @functools.wraps(function)
    async def f(*args, **kwargs):
        assert 'orm' not in kwargs, '"orm" keyword has been occupied'
        kwargs.update({'orm': ReplicationManager.instance().get()})
        retval = await function(*args, **kwargs)
        return retval
    return f


class BaseModel(peewee.Model):

    class Meta:
        database = peewee.PostgresqlDatabase(None)
