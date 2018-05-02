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
from setuptools import setup, find_packages

package = 'tornado_battery'
version = '0.5.17'

setup(
    name=package,
    version=version,
    description="a set of utilities help write tornado apps quickly and easily",
    url='https://github.com/jianingy/tornado_battery',
    setup_requires=['pytest-runner'],
    packages=find_packages(),
    install_requires=[
        'tornado',
        'ujson',
        'colorlog',
        'aioredis',
        'aiopg',
        'aiomysql',
        'aio-pika',
        'uvloop',
    ],
)
