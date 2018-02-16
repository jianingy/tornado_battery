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
from tornado_battery.extra import try_get_value
from unittest import TestCase


class TestTryGetValue(TestCase):

    tree = {
        "1": {
            "A": {
                "a": "value"
            },
            "B": "Bvalue"
        }
    }

    def test_last_node(self):
        self.assertEqual(try_get_value(self.tree, "1.A.a", None), "value")

    def test_last_non_exists(self):
        self.assertEqual(try_get_value(self.tree, "1.A.b", "n/a"), "n/a")

    def test_middle_non_exists(self):
        self.assertEqual(try_get_value(self.tree, "1.c.a", "n/a"), "n/a")

    def test_middle_node(self):
        self.assertEqual(try_get_value(self.tree, "1.B", "n/a"), "Bvalue")

    def test_empty(self):
        self.assertEqual(try_get_value(self.tree, "", "n/a"), "n/a")
