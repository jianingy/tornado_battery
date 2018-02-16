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
    error_format = "a non-format message"


class SimpleFormatException(GeneralException):
    error_format = "an exception: %(reason)s"


class NoMessageException(GeneralException):
    pass


class ErrorCodeException(GeneralException):
    error_code = 40001


def test_non_format_exception():
    match = r"^a non-format message$"
    with pytest.raises(NonFormatException, match=match):
        raise NonFormatException()


def test_format_exception():
    match = "^an exception: something wrong$"
    with pytest.raises(SimpleFormatException, match=match):
        raise SimpleFormatException(reason="something wrong")


def test_error_format_exception():
    match = ("^cannot format exception message: "
             "'an exception: %\(reason\)s'$")
    with pytest.raises(SimpleFormatException, match=match):
        raise SimpleFormatException(other="something wrong")


def test_no_message_exception():
    match = "application exception occurred: something wrong"
    with pytest.raises(NoMessageException, match=match):
        raise NoMessageException(reason="something wrong")


def test_error_code_exception():
    match = "application exception occurred: something wrong"
    with pytest.raises(ErrorCodeException, match=match) as ei:
        raise ErrorCodeException(reason="something wrong", error_code=4001)
    assert ei.value.error_code == 4001


def test_error_code_set():
    match = "application exception occurred: something wrong"
    with pytest.raises(NoMessageException, match=match) as ei:
        raise NoMessageException(reason="something wrong", error_code=4002)
    assert ei.value.error_code == 4002
