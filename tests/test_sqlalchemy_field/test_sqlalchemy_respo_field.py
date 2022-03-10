from typing import Any, AsyncGenerator

import pytest
from sqlalchemy import Column, Integer, String, select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.session import sessionmaker

from respo import RespoClient
from respo.fields.sqlalchemy import SQLAlchemyRespoColumn

Base: Any = declarative_base()


class TheModel(Base):
    __tablename__ = "themodel"
    id = Column(Integer, primary_key=True, index=True)
    respo_field = SQLAlchemyRespoColumn
    name = Column(String(128), nullable=False, server_default="Ursula")


@pytest.fixture
async def test_db_setup():

    async_engine = create_async_engine("sqlite+aiosqlite:///", pool_pre_ping=True)
    async_session = sessionmaker(
        async_engine, expire_on_commit=False, class_=AsyncSession
    )
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

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

    assert new_obj.respo_field.dict() == respo_client.dict()


respo1 = RespoClient()
respo2 = RespoClient()
respo2.add_organization("xxxxx")


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
    assert new_obj.respo_field.add_organization("test_org", validate_input=False)
    assert not new_obj.respo_field.add_organization("test_org", validate_input=False)
    assert new_obj.respo_field.add_role("test_org.test_role", validate_input=False)
    assert not new_obj.respo_field.add_role("test_org.test_role", validate_input=False)

    session.add(new_obj)
    await session.commit()
    await session.refresh(new_obj)

    stmt = select(TheModel).where(TheModel.name == "Respo")
    result = await session.execute(statement=stmt)

    obj: TheModel = result.scalars().one()
    assert "test_org" in obj.respo_field.organizations()
    assert "test_org.test_role" in obj.respo_field.roles()

    assert not obj.respo_field.remove_organization("xyz", validate_input=False)
    assert obj.respo_field.remove_organization("test_org", validate_input=False)
    assert obj.respo_field.remove_role("test_org.test_role", validate_input=False)
    assert not obj.respo_field.remove_role("test_org.test_role", validate_input=False)
    session.add(new_obj)
    await session.commit()
    await session.refresh(new_obj)

    assert new_obj.respo_field.dict() == respo_client.dict()


async def test_respo_field_empty_none_creating(session: AsyncSession):

    new_obj = TheModel(name="Respo")
    session.add(new_obj)
    await session.commit()
    await session.refresh(new_obj)

    stmt = select(TheModel).where(TheModel.name == "Respo")
    result = await session.execute(statement=stmt)

    obj: TheModel = result.scalars().one()
    assert new_obj.respo_field.add_organization("test_org", validate_input=False)
    assert new_obj.respo_field.add_role("test_org.test_role", validate_input=False)
    assert "test_org" in obj.respo_field.organizations()
    assert "test_org.test_role" in obj.respo_field.roles()


async def test_respo_field_cant_bind_bad_value(session: AsyncSession):
    with pytest.raises(ValueError):
        TheModel(respo_field="xyz")
