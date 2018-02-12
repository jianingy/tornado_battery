# -*- coding: utf-8 -*-
#
#        H A P P Y    H A C K I N G !
#              _____               ______
#     ____====  ]OO|_n_n__][.      |    |
#    [________]_|__|________)<     |YANG|
#     oo    oo  'oo OOOO-| oo\\_   ~o~~o~
# +--+--+--+--+--+--+--+--+--+--+--+--+--+
#               Jianing Yang @  8 Feb, 2018
#
from tornado_battery import disable_tornado_logging_options  # noqa
from tornado_battery.command import CommandMixin
from tornado_battery.controller import JSONController
from tornado_battery.route import route
from tornado_battery.postgres import register_postgres_options, PostgresConnector
from tornado.options import options
from tornado.web import Application as WebApplication
import logging

LOG = logging.getLogger("app.biz")


class DBMixin:

    def master_connection(self):
        return PostgresConnector.instance("master").connection()

    def slave_connection(self):
        return PostgresConnector.instance("slave").connection()


@route("/api/v1/greetings")
class AddController(JSONController, DBMixin):

    async def get(self):
        with (await self.slave_connection()) as db:
            cursor = await db.execute("SELECT quote FROM quotes ORDER BY RANDOM()")
            row = cursor.fetchone()
        self.reply(quote=row[0])

    async def post(self):
        with (await self.master_connection()) as db:
            await db.execute("INSERT INTO quotes(quote) VALUES(%(quote)s)",
                             dict(quote=self.data["quote"]))
        self.reply(status="OK")


class GreetingServer(CommandMixin):

    def setup(self, io_loop):
        register_postgres_options("master", "postgres://devel:devel@localhost/devel")
        register_postgres_options("slave", "postgres://devel:devel@localhost/devel")

    def before_run(self, io_loop):
        io_loop.run_sync(PostgresConnector.instance("master").connect)
        io_loop.run_sync(PostgresConnector.instance("slave").connect)
        app = WebApplication(route.get_routes(), autoreload=options.debug)
        app.listen(8000, "0.0.0.0")
        LOG.info("server started.")


start_server = GreetingServer()
