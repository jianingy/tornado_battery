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
from . import routes
from tornado_battery import disable_tornado_logging_options  # noqa
from tornado_battery.entry import HTTPServerEntryBase
from tornado_battery.postgres import (register_postgres_options,
                                      connect_postgres)


class GreetingServer(HTTPServerEntryBase):

    routes = routes

    def init_options(self, io_loop):
        register_postgres_options('master',
                                  'postgres://devel:d3v3l@localhost/devel')
        register_postgres_options('slave',
                                  'postgres://devel:d3v3l@localhost/devel')

    def init_app(self, io_loop):
        io_loop.run_sync(connect_postgres('master'))
        io_loop.run_sync(connect_postgres('slave'))


start = GreetingServer()
