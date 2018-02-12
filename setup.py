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
from setuptools import setup

package = 'tornado_battery'
version = '0.2.1'

setup(name=package,
      version=version,
      description="a set of utilities help write tornado apps quickly and easily",
      url='https://github.com/jianingy/tornado_battery',
      install_requires=['tornado>=4.5.3',
                        'ujson>=1.3.5',
                        'colorlog>=3.1.2',
                        'aioredis>=1.0.0',
                        'momoko>=2.2.4'])
