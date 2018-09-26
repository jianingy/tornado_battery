# -*- coding: UTF-8 -*-
from base64 import (urlsafe_b64encode as b64encode,
                    urlsafe_b64decode as b64decode)
from Crypto import Random
from Crypto.Cipher import AES
from hashlib import sha1
from ujson import loads as json_decode, dumps as json_encode
import hashlib
import hmac

from tornado_battery.exception import ClientException


class InvalidSecureTokenError(ClientException):
    error_code = 400001
    error_format = 'Invalid Token'


class InvalidSecureTokenSignatureError(ClientException):
    error_code = 400001
    error_format = 'Invalid Token Signature'


def _pad(s, size=16):
    return s + (size - len(s) % size) * chr(size - len(s) % size)


def _unpad(s):
    return s[:-ord(s[len(s) - 1:])]


def _key(key):
    return sha1(key.encode('utf8')).hexdigest()[:32]


def _hmac(message, key):
    key = bytes(key, 'UTF-8')
    message = bytes(message, 'UTF-8')
    return b64encode(hmac.new(key, message, hashlib.sha1).digest())


def encode(data, secret=None):

    # Remove trailling padding characters for convenience (been URI encoded).
    json_data = json_encode(data)
    sign = str(_hmac(json_data, secret), 'UTF-8').rstrip('=')
    raw = _pad(json_data)
    iv = Random.new().read(AES.block_size)
    cipher = AES.new(_key(secret), AES.MODE_CBC, iv)
    enc = str(b64encode(iv + cipher.encrypt(raw)), 'UTF-8').rstrip('=')
    return f'{enc}.{sign}'


def decode(token, secret=None):

    def _b(s):
        # Pad the incoming base64 before decode
        return s if len(s) % 4 == 0 else s + '=' * (4 - len(s) % 4)

    try:
        enc, sign = token.split('.')
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(_key(secret), AES.MODE_CBC, iv)
        raw = b64decode(_b(enc))
        json_data = str(_unpad(cipher.decrypt(raw))[len(iv):], 'UTF-8')
        if str(_hmac(json_data, secret), 'UTF-8') == _b(sign):
            return json_decode(json_data)
        else:
            raise InvalidSecureTokenSignatureError()
    except InvalidSecureTokenSignatureError:
        raise
    except Exception as e:
        raise InvalidSecureTokenError() from e
