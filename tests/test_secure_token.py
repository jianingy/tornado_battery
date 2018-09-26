# -*- coding: UTF-8 -*-
from tornado_battery import secure_token
import pytest


def test_secure_token():
    secret = 'hello, world'
    token = secure_token.encode(dict(a=1, b=2, c=3), secret)
    data = secure_token.decode(token, secret)
    assert data['a'] == 1
    assert data['b'] == 2
    assert data['c'] == 3


def test_secure_token_chars():
    secret = 'hello, world'
    raw = {
        '中文': '测试',
        '!@#$%^&*()-_+': '!@#$%^&*()_+',
    }
    token = secure_token.encode(raw, secret)
    data = secure_token.decode(token, secret)
    for key in raw.keys():
        assert data[key] == raw[key]


def test_secure_invalid_token():
    secret = 'hello, world'
    token = '!@#$%^&*()_+'
    match = 'Invalid Token'
    with pytest.raises(secure_token.InvalidSecureTokenError, match=match):
        secure_token.decode(token, secret)


def test_secure_invalid_token_signature():

    secret = 'hello, world'
    raw = {
        '中文': '测试',
        '!@#$%^&*()-_+': '!@#$%^&*()_+',
    }
    token = secure_token.encode(raw, secret)
    enc, sig = token.split('.')
    token = enc + '.eHh4'
    match = 'Invalid Token Signature'
    with pytest.raises(secure_token.InvalidSecureTokenSignatureError,
                       match=match):
        secure_token.decode(token, secret)
