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
from tornado.options import define, options
from tornado.options import parse_config_file

import logging
import tornado

define("debug", group="main", default=False, help="enable debug")
define("config", help="path to config file", group='main',
       callback=lambda path: parse_config_file(path, final=False))


DEFAULT_LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'colorlog': {
            '()': 'colorlog.ColoredFormatter',
            'format': ('%(log_color)s<%(process)d>[%(levelname)1.1s '
                       '%(asctime)s %(module)s:%(lineno)d] '
                       '%(message)s%(reset)s'),
            'datefmt': '%y%m%d %H:%M:%S',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'colorlog',
        },
    },
    'loggers': {
        '': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True
        },
        'app.biz': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False
        },
    }
}


class CommandMixin:

    def enable_logging(self):
        if options.debug:
            level = 'DEBUG'
        else:
            level = options.logging.upper()
            logger = logging.getLogger()
            logger.setLevel(getattr(logging, level))

    def before_run(self, io_loop):
        pass

    def __call__(self):
        from tornado.options import parse_command_line

        io_loop = tornado.ioloop.IOLoop.current()
        parse_command_line()
        self.enable_logging()
        self.before_run(io_loop)
        io_loop.start()
