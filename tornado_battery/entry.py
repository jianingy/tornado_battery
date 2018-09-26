# -*- coding: UTF-8 -*-
#
#        H A P P Y    H A C K I N G !
#              _____               ______
#     ____====  ]OO|_n_n__][.      |    |
#    [________]_|__|________)<     |YANG|
#     oo    oo  'oo OOOO-| oo\\_   ~o~~o~
# +--+--+--+--+--+--+--+--+--+--+--+--+--+
#               Jianing Yang @  26 Sep, 2019
#
from tornado_battery import logging

from importlib import import_module
from tornado.ioloop import IOLoop
from tornado.options import define, options
from tornado.options import parse_command_line, parse_config_file
from tornado.web import Application as WebApplication
import pkgutil
import random


class HTTPServerEntryBase:

    routes = None

    def _init_options(self, io_loop):
        define('config', type=str, default='.config',
               help='path to server configuration',
               callback=lambda path: parse_config_file(path, final=False))
        define('logging', type=str, default='INFO',
               help='default logging level',
               callback=lambda path: parse_config_file(path, final=False))
        define('debug', default=False, type=bool, group='app',
               help='enable debug moed')
        define('bind', default='127.0.0.1:8000', type=str, group='app',
               help='server bind address')
        define('secret', default=None, type=str, group='app', help='加密用秘钥')

        if hasattr(self, 'init_options'):
            return self.init_options(io_loop)
        else:
            return None

    def _init_app(self, io_loop):
        assert self.routes is not None, 'routes not set'
        logging.setup()
        for _, name, _ in pkgutil.iter_modules(self.routes.__path__):
            logging.PLOG.debug(f'importing routes from {name} ...')
            import_module(f'{self.routes.__name__}.{name}',
                          package=__package__)
        self.app = WebApplication(handlers=self.routes.route.get_routes(),
                                  autoreload=options.debug)
        random.seed()

        if hasattr(self, 'init_app'):
            return self.init_app(io_loop)
        else:
            return None

    def start(self, io_loop=None):
        if io_loop is None:
            io_loop = IOLoop.current()
        self._init_options(io_loop)
        parse_command_line()
        self._init_app(io_loop)
        bind_address, _, bind_port = options.bind.partition(':')
        self.app.listen(int(bind_port or 8000), bind_address)
        logging.PLOG.info(f'listening on {bind_address}:{bind_port}.')
        io_loop.start()

    def __call__(self):
        return self.start()
