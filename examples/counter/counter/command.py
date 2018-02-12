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
from tornado_battery.redis import register_redis_options, RedisConnector
from tornado.options import options
from tornado.web import Application as WebApplication
import logging

LOG = logging.getLogger("app.biz")


class RedisMixin:

    def master_redis(self):
        return RedisConnector.instance("master").connection()

    def slave_redis(self):
        return RedisConnector.instance("slave").connection()


@route("/api/v1/counter")
class AddController(JSONController, RedisMixin):

    async def get(self):
        name = self.get_argument("name", "default")
        async with self.slave_redis() as db:
            value = await db.execute('get', 'counter-%s' % name)
        self.reply(name=name, counter=value)

    async def post(self):
        name = self.get_argument("name", "default")
        async with self.slave_redis() as db:
            value = await db.execute('incr', 'counter-%s' % name)
        self.reply(name=name, counter=value)


class GreetingServer(CommandMixin):

    def setup(self, io_loop):
        register_redis_options("master", "redis://localhost/0")
        register_redis_options("slave", "redis://localhost/0")

    def before_run(self, io_loop):
        io_loop.run_sync(RedisConnector.instance("master").connect)
        io_loop.run_sync(RedisConnector.instance("slave").connect)
        app = WebApplication(route.get_routes(), autoreload=options.debug)
        app.listen(8000, "0.0.0.0")
        LOG.info("server started.")


start_server = GreetingServer()
