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
from tornado_battery.route import route
from tornado_battery.controller import JSONController
from tornado.options import options
from tornado.web import Application as WebApplication
import logging

LOG = logging.getLogger("app.biz")


@route("/api/v1/add")
class AddController(JSONController):

    def get(self):
        self.reply(result=int(self.data['x']) + int(self.data['y']))


@route("/api/v1/mul", name="mul")
class MulController(JSONController):

    def post(self):
        self.reply(result=int(self.data['x']) * int(self.data['y']))


@route("/api/v1/times", redirect="/api/v1/mul")
class TimesController(JSONController):
    pass


@route("/api/v1/div")
class DivController(JSONController):

    def post(self):
        self.reply(result=int(self.data['x']) / int(self.data['y']))


class CalcServer(CommandMixin):

    def before_run(self, io_loop):
        app = WebApplication(route.get_routes(), autoreload=options.debug)
        app.listen(8000, "0.0.0.0")
        LOG.info("server started.")


start_server = CalcServer()
