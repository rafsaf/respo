from typing import Optional, TypeVar, TYPE_CHECKING

from sqlalchemy import Column
from sqlalchemy.ext.mutable import Mutable
from sqlalchemy.types import TEXT, TypeDecorator

from respo import core, settings, client


class TEXTRespoField(TypeDecorator):
    """Platform-independent Custom Type to store Respo model based on TEXT type"""

    impl = TEXT
    cache_ok = True

    def process_bind_param(
        self, value: Optional[client.RespoClient], dialect
    ) -> Optional[str]:
        print(value)
        print(type(value))
        if value is None:  # pragma: no cover
            return value
        return str(value)

    def process_result_value(
        self, value: Optional[str], dialect
    ) -> Optional["MutableRespoClient"]:
        return MutableRespoClient(roles_str=value)


class MutableRespoClient(Mutable, client.RespoClient):
    """Mutable Field for RespoClient"""

    @classmethod
    def coerce(cls, key, value):
        if isinstance(value, cls):
            return value
        elif isinstance(value, client.RespoClient):
            return cls(str(value))
        raise ValueError("Field must be instance of RespoClient or MutableRespoClient")

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


class ColumnMixRespoField(Column, MutableRespoClient, str):
    """SQLAlchemy field that represent RespoClient instance, based on TextField.

    It is serialized and deserialized from str to RespoClient and reverse back and forth
    when writing and reading it from database. It *should* be updated in-place by calling methods.
    Note that the default mutation behaviour of ORM was changed here so every add or remove respo client
    method manually trigger self.changed() method.

    Examples:
        >>> from sqlalchemy.ext.declarative import declarative_base
            from respo.fields.sqlalchemy import SQLAlchemyRespoColumn
            Base = declarative_base()
            class TheModel(Base):
                __tablename__ = "themodel"
                id = Column(Integer, primary_key=True, index=True)
                respo_field = SQLAlchemyRespoColumn
                name = Column(String(128), nullable=False, server_default="Ursula")

        In case you need more customization, use _SQLAlchemyRespoField.
        By default column above is declared as follow:

        >>> SQLAlchemyRespoColumn: ColumnMixRespoField = Column(
                _SQLAlchemyRespoField,
                nullable=False,
                server_default="",
                default=get_empty_respo_field,
            )
    """


_SQLAlchemyRespoField = MutableRespoClient.as_mutable(TEXTRespoField)

SQLAlchemyRespoColumn = Column(
    _SQLAlchemyRespoField,
    nullable=False,
    server_default="",
)
