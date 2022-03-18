from typing import Any
from .respo_model import RespoModel
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm.session import sessionmaker
import asyncio
from respo.fields.sqlalchemy import SQLAlchemyRespoColumn

Base: Any = declarative_base()


class TheModel(Base):
    __tablename__ = "my_model"

    id = Column(Integer, primary_key=True)
    respo_field = SQLAlchemyRespoColumn()
    name = Column(String(128), nullable=False, server_default="Ursula")


async def main():
    respo_model = RespoModel.get_respo_model()  # loads respo model from pickled file

    async_engine = create_async_engine(
        "sqlite+aiosqlite:///db.sqlite3", pool_pre_ping=True
    )
    async_session = sessionmaker(
        async_engine, expire_on_commit=False, class_=AsyncSession
    )
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as session:
        new_obj = TheModel(name="Respo")

        session.add(new_obj)
        await session.commit()  # respo_field is stored as string!
        await session.refresh(new_obj)

        new_obj.respo_field.add_role(respo_model.ROLES.ADMIN, respo_model)

        assert new_obj.respo_field.has_permission(
            respo_model.PERMS.USER__READ_BASIC, respo_model
        )


asyncio.run(main())
