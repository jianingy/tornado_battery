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
from tornado.options import options
from typing import Any, Dict


class CORSHandlerMixin:

    def options(self, *args, **kwargs):
        if options.debug:
            self.set_header('Allow', 'POST, GET, PUT, DELETE, OPTIONS, PATCH')

    def set_default_headers(self):
        if options.debug:
            self.set_header('Access-Control-Allow-Origin', '*')
            self.set_header('Access-Control-Allow-Methods',
                            'GET, POST, PUT, DELETE, OPTIONS, HEAD, PATCH')
            self.set_header('Access-Control-Max-Age', '3600')
            self.set_header('Access-Control-Allow-Headers',
                            'Content-Type, Access-Control-Allow-Headers')


def try_get_value(d: Dict[str, Any], path: str, null_value: Any=None):

    current, nodes = d, path.split('.')

    while nodes:
        if not isinstance(current, dict):
            return null_value
        key = nodes.pop(0)
        if key not in current:
            return null_value
        current = current[key]

    return current
