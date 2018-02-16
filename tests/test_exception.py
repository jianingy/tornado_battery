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
from unittest import TestCase


class NonFormatException(GeneralException):
    error_format = "a non-format message"


class SimpleFormatException(GeneralException):
    error_format = "an exception: %(reason)s"


class NoMessageException(GeneralException):
    pass


class ErrorCodeException(GeneralException):
    error_code = 40001


class TestException(TestCase):

    def test_non_format_exception(self):
        match = "^a non-format message$"
        with self.assertRaisesRegex(NonFormatException, match):
            raise NonFormatException()

    def test_format_exception(self):
        match = "^an exception: something wrong$"
        with self.assertRaisesRegex(SimpleFormatException, match):
            raise SimpleFormatException(reason="something wrong")

    def test_error_format_exception(self):
        match = ("^cannot format exception message: "
                 "'an exception: %\(reason\)s'$")
        with self.assertRaisesRegex(SimpleFormatException, match):
            raise SimpleFormatException(other="something wrong")

    def test_no_message_exception(self):
        match = "application exception occurred: something wrong"
        with self.assertRaisesRegex(NoMessageException, match):
            raise NoMessageException(reason="something wrong")

    def test_error_code_exception(self):
        match = "application exception occurred: something wrong"
        with self.assertRaisesRegex(ErrorCodeException, match) as cm:
            raise ErrorCodeException(reason="something wrong", error_code=4001)
        self.assertEqual(cm.exception.error_code, 4001)

    def test_error_code_set(self):
        match = "application exception occurred: something wrong"
        with self.assertRaisesRegex(NoMessageException, match) as cm:
            raise NoMessageException(reason="something wrong", error_code=4002)
        self.assertEqual(cm.exception.error_code, 4002)
