# -*- coding: utf-8 -*-
#
#        H A P P Y    H A C K I N G !
#              _____               ______
#     ____====  ]OO|_n_n__][.      |    |
#    [________]_|__|________)<     |YANG|
#     oo    oo  'oo OOOO-| oo\\_   ~o~~o~
# +--+--+--+--+--+--+--+--+--+--+--+--+--+
#               Jianing Yang @ 17 Feb, 2018
#
from .exception import ServerException
from .pattern import NamedSingletonMixin
from aio_pika import connect_robust, Message
from tornado.options import define, options
from typing import Any
from ujson import dumps as json_encode, loads as json_decode

import asyncio
import logging

LOG = logging.getLogger('tornado.application')


class QueueConnectorError(ServerException):
    error_code = 602001


class QueueConnector(NamedSingletonMixin):

    def __init__(self, name):
        self.name = name

    async def connect(self, event_loop=None):
        if event_loop is None:
            event_loop = asyncio.get_event_loop()
        name = self.name
        opts = options.group_dict(f'{name} queue')
        uri = opts[option_name(name, 'uri')]
        LOG.info(f'connecting amqp [{self.name} {uri}')
        self._connection = await connect_robust(uri, loop=event_loop)

    def connection(self):
        if not hasattr(self, '_connection') or not self._connection:
            raise QueueConnectorError(f'no connection of {self.name} found')
        return self._connection


class JSONQueueError(ServerException):
    error_code = 602002


class JSONQueue(QueueConnector):

    async def setup(self, queue: str=None, exchange: str='',
                    routing_key: str='', durable: bool=False):
        channel = await self.connection().channel()
        exchange = await channel.declare_exchange(exchange)
        if queue:
            queue = await channel.declare_queue(queue, auto_delete=True,
                                                durable=durable)
            await queue.bind(exchange, routing_key)
            self.active_queue = queue
        self.routing_key = routing_key
        self.active_exchange = exchange

    async def publish(self, content: Any):
        if not hasattr(self, 'active_exchange'):
            raise JSONQueueError('no active exchange set')

        message = Message(bytes(json_encode(content), 'utf-8'),
                          content_type='application/json')
        await self.active_exchange.publish(message, self.routing_key)

    async def consume(self):
        if not hasattr(self, 'active_queue'):
            raise JSONQueueError('no active queue set')

        msg = await self.active_queue.get()
        if msg.content_type != 'application/json':
            msg.reject(requeue=False)
            return None
        try:
            data = json_decode(msg.body)
        except ValueError as e:
            msg.reject(requeue=False)
            return None
        return data, msg


def option_name(instance: str, option: str) -> str:
    return f'queue-{instance}-{option}'


def register_queue_options(instance: str='master',
                           default_uri: str='amqp://'):
    define(option_name(instance, 'uri'),
           default=default_uri,
           group=f'{instance} queue',
           help=f'queue connection uri for {instance}')
