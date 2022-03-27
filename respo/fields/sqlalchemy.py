from typing import Optional

from sqlalchemy import Column
from sqlalchemy.ext.mutable import Mutable
from sqlalchemy.types import TEXT, TypeDecorator
from typing_extensions import Self

from respo import client, core, settings


class TEXTRespoField(TypeDecorator):
    """Platform-independent Custom Type to store Respo model based on TEXT type"""

    impl = TEXT
    cache_ok = True

    def process_bind_param(self, value: "MutableRespoClient", dialect) -> str:
        return str(value)

    def process_result_value(
        self, value: Optional[str], dialect
    ) -> "MutableRespoClient":
        return MutableRespoClient(roles_str=value)


class MutableRespoClient(Mutable, client.RespoClient):
    """SQLAlchemy field that represent RespoClient instance, based on Mutable.

    Wrapper around RespoClient instance that triggers changed() on
    add_role and remove_role. Overwrittes ORM that use fancy mechanisms
    that won't detect mutable objects changes (and won't be commited to database).

    https://docs.sqlalchemy.org/en/14/orm/extensions/mutable.html
    """

    @classmethod
    def coerce(cls, key, value):
        """Transforms Python object to MutableRespoClient Field."""

        if isinstance(value, cls):
            return value
        elif isinstance(value, client.RespoClient):
            return cls(str(value))
        raise ValueError("Field must be instance of RespoClient or MutableRespoClient.")

    def add_role(
        self,
        role_name: str,
        respo_model: Optional[core.RespoModel] = None,
        validate_input: bool = settings.config.RESPO_CHECK_FORCE,
    ) -> bool:
        res = super().add_role(role_name, respo_model, validate_input)
        self.changed()
        return res

    def remove_role(
        self,
        role_name: str,
        respo_model: Optional[core.RespoModel] = None,
        validate_input: bool = settings.config.RESPO_CHECK_FORCE,
    ) -> bool:
        res = super().remove_role(role_name, respo_model, validate_input)
        self.changed()
        return res


class MutableRespoColumn(Column, MutableRespoClient):
    pass


_SQLAlchemyRespoField = MutableRespoClient.as_mutable(TEXTRespoField)


class SQLAlchemyRespoColumn(Column, MutableRespoClient):
    def __new__(cls) -> Self:
        return Column(
            _SQLAlchemyRespoField,
            nullable=False,
            server_default="",
        )  # type: ignore
