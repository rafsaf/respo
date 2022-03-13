from typing import Any, AsyncGenerator

import pytest
from sqlalchemy import Column, Integer, String, select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.orm import registry
from respo import RespoClient
from respo.fields.sqlalchemy import ColumnMixRespoField, SQLAlchemyRespoColumn
from dataclasses import dataclass
from dataclasses import field
from typing import List

from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import registry
from sqlalchemy.orm import relationships

mapper_registry = registry()


@mapper_registry.mapped
@dataclass
class TheModel:
    __tablename__ = "themodel"
    __sa_dataclass_metadata_key__ = "sa"

    id: int = field(init=False, metadata={"sa": Column(Integer, primary_key=True)})
    respo_field: RespoClient = field(
        default=RespoClient(), metadata={"sa": SQLAlchemyRespoColumn}
    )
    name: str = field(
        default="Ursula",
        metadata={"sa": Column(String(128), nullable=False, server_default="Ursula")},
    )


@pytest.fixture
async def test_db_setup():

    async_engine = create_async_engine("sqlite+aiosqlite:///", pool_pre_ping=True)
    async_session = sessionmaker(
        async_engine, expire_on_commit=False, class_=AsyncSession
    )
    async with async_engine.begin() as conn:
        await conn.run_sync(mapper_registry.metadata.drop_all)
        await conn.run_sync(mapper_registry.metadata.create_all)

    return async_session


@pytest.fixture
async def session(test_db_setup) -> AsyncGenerator[AsyncSession, None]:
    async with test_db_setup() as session:
        yield session


async def test_respo_field_simple_create_and_change(session: AsyncSession):
    respo_client = RespoClient()
    new_obj = TheModel(respo_field=respo_client)
    session.add(new_obj)
    await session.commit()
    await session.refresh(new_obj)

    assert new_obj.respo_field.roles == respo_client.roles


respo1 = RespoClient()
respo2 = RespoClient()
respo2.add_role("xxxxx", validate_input=False)


@pytest.mark.parametrize(
    "respo_client",
    [
        (respo1),
        (respo2),
    ],
)
async def test_respo_field_handles_methods(
    session: AsyncSession, respo_client: RespoClient
):

    new_obj = TheModel(respo_field=respo_client, name="Respo")
    assert new_obj.respo_field.add_role("test_role", validate_input=False)
    assert not new_obj.respo_field.add_role("test_role", validate_input=False)

    session.add(new_obj)
    await session.commit()
    await session.refresh(new_obj)

    stmt = select(TheModel).where(TheModel.name == "Respo")
    result = await session.execute(statement=stmt)

    obj: TheModel = result.scalars().one()
    assert "test_role" in obj.respo_field.roles

    assert obj.respo_field.remove_role("test_role", validate_input=False)
    session.add(new_obj)
    await session.commit()
    await session.refresh(new_obj)

    assert new_obj.respo_field.roles == respo_client.roles


async def test_respo_field_empty_none_creating(session: AsyncSession):

    new_obj = TheModel(name="Respo")
    session.add(new_obj)
    await session.commit()
    await session.refresh(new_obj)
    new_obj.name = ""

    stmt = select(TheModel).where(TheModel.name == "Respo")
    result = await session.execute(statement=stmt)

    obj: TheModel = result.scalars().one()
    assert new_obj.respo_field.add_role("test_role", validate_input=False)
    assert "test_role" in obj.respo_field.roles


async def test_respo_field_bind(session: AsyncSession):

    new_obj = TheModel(name="Respo")
    session.add(new_obj)
    await session.commit()
    await session.refresh(new_obj)

    stmt = select(TheModel).where(TheModel.name == "Respo")
    result = await session.execute(statement=stmt)

    obj: TheModel = result.scalars().one()
    obj.respo_field = RespoClient()
