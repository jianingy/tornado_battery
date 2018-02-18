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
from typing import Any, Dict


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
