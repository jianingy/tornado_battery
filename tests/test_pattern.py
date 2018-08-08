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
from tornado_battery.pattern import SingletonMixin, NamedSingletonMixin


class Single1(SingletonMixin):
    pass


class Single2(SingletonMixin):
    pass


class NamedSingle1(NamedSingletonMixin):

    def __init__(self, name):
        self.name = name


class NamedSingle2(NamedSingletonMixin):

    def __init__(self, name):
        self.name = name


def test_singleton():
    Single2.instance()
    instance_id = id(Single1.instance())
    ids = [id(Single1.instance()) == instance_id for i in range(0, 100)]
    assert all(ids)
    assert id(Single1.instance()) != id(Single2.instance())


def test_named_singleton():
    NamedSingle2.instance('master')
    NamedSingle2.instance('slave')
    master_id = id(NamedSingle1.instance('master'))
    master_ids = [id(NamedSingle1.instance('master')) == master_id
                  for i in range(0, 100)]
    assert all(master_ids)

    slave_id = id(NamedSingle1.instance('slave'))
    slave_ids = [id(NamedSingle1.instance('slave')) == slave_id
                 for i in range(0, 100)]
    assert all(slave_ids)

    assert master_id != slave_id
    assert (id(NamedSingle1.instance('master')) !=
            id(NamedSingle2.instance('master')))
    assert (id(NamedSingle1.instance('slave')) !=
            id(NamedSingle2.instance('slave')))
