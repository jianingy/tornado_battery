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
from tornado_battery.cassandra import (
    register_cassandra_options,
    with_cassandra,
    CassandraConnector,
    CassandraConnectorError)
import logging

LOG = logging.getLogger("tornado.application")


@route("/api/v1/user")
class UserController(JSONController):

    @with_cassandra(name='test')
    async def get(self, cassandra):
        query = await cassandra.prepare_future('SELECT * FROM tornado.users')
        retval = await cassandra.execute_future(query)
        self.reply(retval=retval)

    @with_cassandra(name='test')
    async def post(self, cassandra):
        username = self.get_data('username', None)
        mobile = self.get_data('mobile', None)
        stmt = 'INSERT INTO tornado.users(mobile, username) VALUES (%s, %s)'
        retval = await cassandra.execute_future(stmt, [mobile, username])
        self.reply(retval=retval)


class AccountServer(CommandMixin):

    def setup(self):
        register_cassandra_options('test')

    def before_run(self, io_loop):
        io_loop.run_sync(CassandraConnector.instance('test').connect)
        app = WebApplication(route.get_routes(), autoreload=options.debug)
        app.listen(8000, "0.0.0.0")
        LOG.info("server started.")


start_server = AccountServer()
