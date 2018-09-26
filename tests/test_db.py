# -*- coding: utf-8 -*-
from tornado.gen import multi
from asyncio import sleep
from datetime import datetime
import peewee
import pytest

from tornado_battery.db import (
    with_orm,
    use_orm,
    Replications,
    ReplicationManager,
    BaseModel)

pytestmark = pytest.mark.asyncio


class User(BaseModel):

    openid = peewee.CharField(max_length=60)
    sex = peewee.IntegerField()
    created_at = peewee.DateTimeField(default=datetime.now)

    class Meta:
        db_table = 'users'


@pytest.fixture
async def db():
    repl = Replications.instance()
    repl.add('master', 'postgres://test:test@127.0.0.1/test')
    repl.add('slave', 'postgres://test:test@127.0.0.1/test')
    with pytest.raises(NotImplementedError, match='only support postgresql'):
        repl.add('error', 'mysql://test:test@127.0.0.1/test')
    man = ReplicationManager.instance()
    man.initialize()


async def test_orm_stack(db):

    orms = []

    @use_orm('master')
    @with_orm
    async def _within_master(orm):
        orms.append(orm)

    @use_orm('slave')
    @with_orm
    async def _within_slave(orm):
        orms.append(orm)

    @use_orm('master')
    @with_orm
    async def _run(orm):
        orms.append(orm)
        await _within_master()
        await _within_slave()
        orms.append(orm)

    await _run()
    assert orms[0] == orms[3]
    assert orms[0] == orms[1]
    assert orms[2] != orms[0]


async def test_orm_stack_async(db):

    orms = []

    @use_orm('master')
    @with_orm
    async def _within_master(orm):
        await sleep(0.5)
        orms.append(orm)

    @use_orm('slave')
    @with_orm
    async def _within_slave(orm):
        await sleep(0.2)
        orms.append(orm)

    @use_orm('master')
    @with_orm
    async def _run(orm):
        orms.append(orm)
        done, _ = await multi([_within_master(), _within_slave()])
        orms.append(orm)

    await _run()
    assert orms[0] == orms[3]
    assert orms[0] != orms[1]
    assert orms[0] == orms[2]


async def test_orm_model(db):

    @use_orm('master')
    @with_orm
    async def _run(orm):
        await orm.execute(User.raw("""
            CREATE TABLE IF NOT EXISTS users(
            id SERIAL PRIMARY KEY, openid VARCHAR(60),
            sex INT, created_at TIMESTAMP); TRUNCATE TABLE users; SELECT 1"""))
        await orm.create(User, openid='XXX', sex=0,
                         created_at='2018-01-01 00:00:00')
        user = await orm.get(User.select())
        assert user.openid == 'XXX'
        assert user.sex == 0
        assert user.created_at == datetime(2018, 1, 1, 0, 0)

    await _run()
