# main.py

import random

from fastapi import Depends, FastAPI, HTTPException
import asyncio
from respo import RespoClient
from dataclasses import dataclass, field
from .respo_model import RespoModel
from sqlalchemy import Column, Integer, String, select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import registry
from sqlalchemy.orm.session import sessionmaker


from respo import RespoClient
from respo.fields.sqlalchemy import SQLAlchemyRespoField
from sqlalchemy.sql import func

RESPO_MODEL = RespoModel.get_respo_model()


async_engine = create_async_engine(
    "sqlite+aiosqlite:////tmp/user_have_perms.db", pool_pre_ping=True
)
async_session = sessionmaker(
    async_engine, expire_on_commit=False, class_=AsyncSession  # type: ignore
)
mapper_registry = registry()


@mapper_registry.mapped
@dataclass
class User:
    __tablename__ = "user_model"
    __sa_dataclass_metadata_key__ = "sa"

    id: int = field(
        init=False,
        metadata={"sa": Column(Integer, primary_key=True)},
    )
    name: str = field(
        metadata={"sa": Column(String(254), nullable=False, unique=True, index=True)}
    )
    respo_field: RespoClient = field(
        default_factory=RespoClient,
        metadata={
            "sa": Column(SQLAlchemyRespoField, nullable=False, server_default="")
        },
    )


app = FastAPI()


async def db_setup():
    async with async_engine.begin() as conn:
        await conn.run_sync(mapper_registry.metadata.drop_all)
        await conn.run_sync(mapper_registry.metadata.create_all)

    async with async_session() as session:
        session: AsyncSession
        respo_client_admin = RespoClient()
        respo_client_admin.add_role(RESPO_MODEL.ROLES.ADMIN, RESPO_MODEL)
        respo_client_no_roles = RespoClient()

        user_peter = User("Peter", respo_client_admin)
        user_sara = User("Sara", respo_client_no_roles)

        session.add(user_peter)
        session.add(user_sara)
        await session.commit()


def user_have_permission(permission):
    async def inner_user_have_permission(db_setup=Depends(db_setup)):
        # normally we would get user by access_token from header or
        # another dependency, here we get random user from database
        async with async_session() as session:
            session: AsyncSession
            user: User = (
                (await session.execute(select(User).order_by(func.random()).limit(1)))
                .scalars()
                .one()
            )

        if not user.respo_field.has_permission(permission, RESPO_MODEL):
            raise HTTPException(403)
        return user

    return inner_user_have_permission


@app.get("/")
def get_user(
    user: User = Depends(user_have_permission(RESPO_MODEL.PERMS.USER__READ_ALL)),
):
    return {"name": user.name}
