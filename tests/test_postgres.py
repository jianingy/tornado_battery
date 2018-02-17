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
from tornado_battery.postgres import register_postgres_options, with_postgres
from tornado_battery.postgres import PostgresConnector
import pytest

pytestmark = pytest.mark.asyncio
register_postgres_options("test", "postgres://test:test@127.0.0.1/test")


@pytest.fixture
async def postgres():
    db = PostgresConnector.instance("test")
    await db.connect()
    return db


async def test_select(postgres):

    @with_postgres(name="test")
    async def _select(db):
        async with db.cursor() as cursor:
            await cursor.execute("SELECT 1")
            value = await cursor.fetchone()
            return value

    assert (await _select()) == (1,)
