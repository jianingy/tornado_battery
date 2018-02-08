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
LOG = logging.getLogger("tornado.application")


class SingletonMixin(object):

    __instance_lock = threading.Lock()
    __instance = None

    @classmethod
    def instance(cls):
        if not hasattr(cls, "__instance"):
            with cls.__instance_lock:
                if not hasattr(cls, "__instance"):
                    LOG.debug("create a new instance for '%s'" % cls)
                    setattr(cls, "__instance", cls())
        return cls.__instance


if __name__ == '__main__':

    class Single(SingletonMixin):
        pass

    _id = id(Single.instance())
    print(all([id(Single.instance()) == _id for i in range(0, 100)]))
