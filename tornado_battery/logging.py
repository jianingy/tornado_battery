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

from tornado.options import define, options
import logging
import logging.config

define('logging-config', default=None, type=str, group='app',
       help='path to log configuration')

PLOG = logging.getLogger('app')  # Progarm Log
ZLOG = logging.getLogger('biz')  # Business Logic Log

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
            'propagate': True,
        },
        'app': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'biz': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}


def setup():
    level = 'DEBUG' if options.debug else options.logging.upper()
    logging.config.dictConfig(DEFAULT_LOGGING_CONFIG)
    if options.logging_config:
        logging.config.fileConfig(options.logging_config,
                                  disable_existing_loggers=False)
    logging.getLogger().setLevel(getattr(logging, level))
