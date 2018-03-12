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

package = 'greetings_mysql'
version = '0.1.0'

setup(name=package,
      version=version,
      description="a simple greeting api, use mysql as backend",
      url='https://github.com/jianingy/tornado_battery',
      entry_points={
          'console_scripts': ['greeting-mysql-server=greetings_mysql.command:start_server'],
      },
      install_requires=['tornado_battery'])
