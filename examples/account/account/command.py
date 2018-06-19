# -*- coding: utf-8 -*-
from tornado_battery import disable_tornado_logging_options  # noqa
from aiocassandra import aiosession
from cassandra.cluster import Cluster
from tornado.options import options
from tornado.web import Application as WebApplication
from tornado_battery.command import CommandMixin
from tornado_battery.controller import JSONController
from tornado_battery.pattern import SingletonMixin
from tornado_battery.route import route
import logging

LOG = logging.getLogger("tornado.application")


class CassandraCluster(SingletonMixin):

    def __init__(self):
        self._cluster = Cluster(executor_threads=4)

    def connect(self):
        self._session = aiosession(self._cluster.connect())

    def session(self):
        return self._session


@route("/api/v1/user")
class UserController(JSONController):

    async def get(self):
        session = CassandraCluster().instance().session()
        stmt = 'SELECT * FROM tornado.users'
        retval = await session.execute_future(stmt)
        self.reply(retval=retval)

    async def post(self):
        username = self.get_data('username', None)
        mobile = self.get_data('mobile', None)
        session = CassandraCluster().instance().session()
        stmt = 'INSERT INTO tornado.users(mobile, username) VALUES (%s, %s)'
        retval = await session.execute_future(stmt, [mobile, username])
        self.reply(retval=retval)


class AccountServer(CommandMixin):

    def setup(self):
        CassandraCluster().instance().connect()

    def before_run(self, io_loop):
        app = WebApplication(route.get_routes(), autoreload=options.debug)
        app.listen(8000, "0.0.0.0")
        LOG.info("server started.")


start_server = AccountServer()
