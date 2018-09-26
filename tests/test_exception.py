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
from tornado_battery.exception import GeneralException
import pytest


class NonFormatException(GeneralException):
    error_code = 50001
    error_format = 'a non-format message'


class SimpleFormatException(GeneralException):
    error_code = 50002
    error_format = 'an exception: %(reason)s'


class NoMessageException(GeneralException):
    error_code = 50003


class ErrorCodeException(GeneralException):
    error_code = 40001


def test_non_format_exception():
    match = r'^a non-format message$'
    with pytest.raises(NonFormatException, match=match):
        raise NonFormatException()


def test_format_exception():
    match = '^an exception: something wrong$'
    with pytest.raises(SimpleFormatException, match=match):
        raise SimpleFormatException(reason='something wrong')


def test_error_format_exception():
    match = ('^cannot format exception: '
             'an exception: %\(reason\)s$')
    with pytest.raises(SimpleFormatException, match=match):
        raise SimpleFormatException(other='something wrong')


def test_no_message_exception():
    match = 'application exception occurred: something wrong'
    with pytest.raises(NoMessageException, match=match):
        raise NoMessageException(reason='something wrong')


def test_error_code_exception():
    match = 'application exception occurred: something wrong'
    with pytest.raises(ErrorCodeException, match=match) as ei:
        raise ErrorCodeException(reason='something wrong')
    assert ei.value.error_code == 40001


def test_duplicate_error_code():

    class ErrorA(GeneralException):
        error_code = 401001

    class ErrorB(GeneralException):
        error_code = 401001
