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
from tornado_battery.mysql import register_mysql_options, with_mysql, connect_mysql
from tornado.options import options
from tornado.web import Application as WebApplication
import logging

LOG = logging.getLogger("app.biz")


@route("/api/v1/greetings_mysql")
class AddController(JSONController):

    @with_mysql(name="slave")
    async def get(self, db):
        async with db.cursor() as cursor:
            await cursor.execute("SELECT quote FROM quotes ORDER BY RAND()")
            row = await cursor.fetchone()
        self.reply(quote=row[0])

    @with_mysql(name="master")
    async def post(self, db):
        async with db.cursor() as cursor:
            await cursor.execute("INSERT INTO quotes(quote) VALUES(%(quote)s)",
                                 dict(quote=self.data["quote"]))
        self.reply(status="OK")


class GreetingServer(CommandMixin):

    def setup(self, io_loop):
        register_mysql_options("master", "mysql://root:root@172.17.0.2/test")
        register_mysql_options("slave", "mysql://root:root@172.17.0.2/test")

    def before_run(self, io_loop):
        io_loop.run_sync(connect_mysql("master"))
        io_loop.run_sync(connect_mysql("slave"))

        app = WebApplication(route.get_routes(), autoreload=options.debug)
        app.listen(8000, "0.0.0.0")
        LOG.info("server started.")


start_server = GreetingServer()


if __name__ == "__main__":
    start_server()
