# -*- coding: utf-8 -*-
#
#        H A P P Y    H A C K I N G !
#              _____               ______
#     ____====  ]OO|_n_n__][.      |    |
#    [________]_|__|________)<     |YANG|
#     oo    oo  'oo OOOO-| oo\\_   ~o~~o~
# +--+--+--+--+--+--+--+--+--+--+--+--+--+
#               Jianing Yang @ 18 Feb, 2018
#
from tornado_battery.queue import register_queue_options, QueueConnectorError
from tornado_battery.queue import JSONQueue, JSONQueueError
import pytest

pytestmark = pytest.mark.asyncio
register_queue_options('test', 'amqp://guest:guest@127.0.0.1:5672/%2F')
register_queue_options('vanilla', 'amqp://guest:guest@127.0.0.1:5672/%2F')


@pytest.fixture
async def queue():
    pika = JSONQueue.instance('test')
    await pika.connect()
    return pika


@pytest.fixture
async def vanilla_queue():
    pika = JSONQueue.instance('vanilla')
    await pika.connect()
    return pika


async def test_publish_consume(queue):
    await queue.setup(queue='test_queue', exchange='test_exchange')
    await queue.publish(dict(value=1984))

    data, msg = await queue.consume()
    msg.ack()
    assert data == dict(value=1984)


async def test_no_setup_publish(vanilla_queue):
    with pytest.raises(JSONQueueError, match='^no active exchange set$'):
        await vanilla_queue.publish(dict(value=1984))


async def test_no_setup_consume(vanilla_queue):
    with pytest.raises(JSONQueueError, match='^no active queue set$'):
        await vanilla_queue.consume()


async def test_no_connection():
    match = r'^no connection of noconn found$'
    with pytest.raises(QueueConnectorError, match=match):
        JSONQueue.instance('noconn').connection()


async def test_option_name():
    from tornado_battery.queue import option_name

    assert option_name('master', 'uri') == 'queue-master-uri'
    assert option_name('slave', 'uri') == 'queue-slave-uri'
