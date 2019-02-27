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
from os.path import dirname, realpath, join as path_join
from setuptools import setup, find_packages

package = 'tornado_battery'
version = '0.8.1'


def valid_requirement(line):
    if not line:
        return False
    else:
        ch = line[0]
        return ch not in ('#', '-')


def parse_requirements(filename):
    """ load requirements from a pip requirements file """
    root = dirname(realpath(__file__))
    line_iter = (line.strip() for line in open(path_join(root, filename)))
    return [line for line in line_iter if valid_requirement(line)]


setup(
    name=package,
    version=version,
    description='utilities that help write tornado apps quickly and easily',
    url='https://github.com/jianingy/tornado_battery',
    setup_requires=['pytest-runner'],
    packages=find_packages(),
    install_requires=parse_requirements('requirements.txt'),
)
