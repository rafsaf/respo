import asyncio
from dataclasses import dataclass, field

from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import registry

from respo import RespoClient
from respo.fields.sqlalchemy import SQLAlchemyRespoField

from .respo_model import RespoModel

Base = registry()


@Base.mapped
@dataclass
class ExampleModel:
    __tablename__ = "example_model"
    __sa_dataclass_metadata_key__ = "sa"

    id: int = field(init=False, metadata={"sa": Column(Integer, primary_key=True)})
    respo_field: RespoClient = field(
        default_factory=RespoClient,
        metadata={
            "sa": Column(SQLAlchemyRespoField, nullable=False, server_default="")
        },
    )
    name: str = field(
        default="Ursula",
        metadata={"sa": Column(String(128), nullable=False, server_default="Ursula")},
    )


async def main():
    respo_model = RespoModel.get_respo_model()  # loads respo model from pickled file

    async_engine = create_async_engine(
        "sqlite+aiosqlite:///db.sqlite3", pool_pre_ping=True
    )
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

        async with AsyncSession(bind=conn) as session:
            new_obj = ExampleModel(name="Respo")
            new_obj.respo_field.add_role(respo_model.ROLES.ADMIN, respo_model)

            session.add(new_obj)
            await session.commit()  # respo_field is stored as a string!
            await session.refresh(new_obj)

            assert new_obj.respo_field.has_permission(
                respo_model.PERMS.USER__READ_BASIC, respo_model
            )


asyncio.run(main())
