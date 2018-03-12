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
from tornado_battery.mysql import register_mysql_options, with_mysql
from tornado_battery.mysql import MysqlConnector, MysqlConnectorError
import pytest
import logging

pytestmark = pytest.mark.asyncio
register_mysql_options("test", "mysql://root:root@172.17.0.2:3306/test")
logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger("test_mysql")

@pytest.fixture
async def mysql():
    db = MysqlConnector.instance("test")
    await db.connect()
    LOG.info("connect success!")
    return db


async def test_select(mysql):

    @with_mysql(name="test")
    async def _select(db):
        async with db.cursor() as cursor:
            await cursor.execute("SELECT 1")
            value = await cursor.fetchone()
            return value

    assert (await _select()) == (1,)


async def test_decorator_duplicated(mysql):

    @with_mysql(name="test")
    async def _select(db):
        async with db.cursor() as cursor:
            await cursor.execute("SELECT 1")
            value = await cursor.fetchone()
            return value
    with pytest.raises(MysqlConnectorError):
        await _select(db=None)


async def test_no_connection():
    match = r"^no connection of noconn found$"
    with pytest.raises(MysqlConnectorError, match=match):
        MysqlConnector.instance("noconn").connection()


async def test_invalid_connection_scheme():
    from tornado.options import options
    options.mysql_test_uri = "test://"
    match = r" is not a mysql connection scheme$"
    with pytest.raises(MysqlConnectorError, match=match):
        await MysqlConnector.instance("test").connect()


async def test_option_name():
    from tornado_battery.mysql import option_name

    assert option_name("master", "uri") == "mysql-master-uri"
    assert option_name("slave", "uri") == "mysql-slave-uri"
