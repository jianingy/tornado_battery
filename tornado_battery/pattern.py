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

import logging
import threading
LOG = logging.getLogger('tornado.application')


class SingletonMixin:

    __instance_lock = threading.Lock()

    @classmethod
    def instance(cls):
        if not hasattr(cls, '__instance'):
            with cls.__instance_lock:
                if not hasattr(cls, '__instance'):
                    LOG.debug(f"create a singleton instance for '{cls}'")
                    setattr(cls, '__instance', cls())

        return getattr(cls, '__instance')


class NamedSingletonMixin:

    __instance_lock = threading.Lock()

    @classmethod
    def instance(cls, name: str):
        if not hasattr(cls, '__instances'):
            with cls.__instance_lock:
                if not hasattr(cls, '__instances'):
                    LOG.debug(f"create a named singleton instance for '{cls}")
                    setattr(cls, '__instances', dict())

        instances = getattr(cls, '__instances')
        if name not in instances:
            with cls.__instance_lock:
                instances[name] = cls(name=name)
        return instances[name]
