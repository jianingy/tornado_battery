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
version = '0.5.19'

def parse_requirements(filename):
    """ load requirements from a pip requirements file """
    lineiter = (line.strip() for line in open(filename))
    return [line for line in lineiter if line and not line.startswith("#")]


setup(
    name=package,
    version=version,
    description='utilities that help write tornado apps quickly and easily',
    url='https://github.com/jianingy/tornado_battery',
    setup_requires=['pytest-runner'],
    packages=find_packages(),
    install_requires=parse_requirements('requirements.txt')
)
