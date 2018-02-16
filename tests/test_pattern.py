# -*- coding: utf-8 -*-
#
#        H A P P Y    H A C K I N G !
#              _____               ______
#     ____====  ]OO|_n_n__][.      |    |
#    [________]_|__|________)<     |YANG|
#     oo    oo  'oo OOOO-| oo\\_   ~o~~o~
# +--+--+--+--+--+--+--+--+--+--+--+--+--+
#               Jianing Yang @ 16 Feb, 2018
#
from tornado_battery.pattern import SingletonMixin
from unittest import TestCase


class Single1(SingletonMixin):
    pass


class Single2(SingletonMixin):
    pass


class TestSingleton(TestCase):

    def test_singleton(self):
        Single2.instance()
        instance_id = id(Single1.instance())
        ids = [id(Single1.instance()) == instance_id for i in range(0, 100)]
        self.assertTrue(all(ids))
