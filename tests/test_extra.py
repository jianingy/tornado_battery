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
import pytest


@pytest.fixture
def data():

    return {
        "1": {
            "A": {
                "a": "value"
            },
            "B": "Bvalue"
        }
    }


def test_last_node(data):
    assert try_get_value(data, "1.A.a", None) == "value"


def test_last_non_exists(data):
    assert try_get_value(data, "1.A.b", "n/a") == "n/a"


def test_middle_non_exists(data):
    assert try_get_value(data, "1.c.a", "n/a") == "n/a"


def test_middle_node(data):
    assert try_get_value(data, "1.B", "n/a") == "Bvalue"


def test_empty(data):
    assert try_get_value(data, "", "n/a") == "n/a"


def test_non_dict():
    assert try_get_value(1, "", "n/a") == "n/a"
