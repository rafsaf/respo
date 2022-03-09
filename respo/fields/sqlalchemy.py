from typing import Optional, Union

from sqlalchemy import Column
from sqlalchemy.ext.mutable import Mutable
from sqlalchemy.types import TEXT, TypeDecorator

from respo.client import RespoClient
from respo.config import config
from respo.respo_model import BaseRespoModel, Organization, Role


class TEXTRespoField(TypeDecorator):
    """Platform-independent Custom Type to store Respo model based on TEXT type"""

    impl = TEXT
    cache_ok = True

    def process_bind_param(
        self, value: Optional[RespoClient], dialect
    ) -> Optional[str]:
        if value is None:  # pragma: no cover
            return value
        return str(value)

    def process_result_value(
        self, value: Optional[str], dialect
    ) -> Optional["MutableRespoClient"]:
        if value is None:  # pragma: no cover
            return value
        return MutableRespoClient(json_string=value)


class MutableRespoClient(Mutable, RespoClient):
    @classmethod
    def coerce(cls, key, value):
        if isinstance(value, cls):
            return value
        elif isinstance(value, RespoClient):
            return cls(str(value))
        raise ValueError("Field must be instance of RespoClient or MutableRespoClient")

    def add_organization(
        self,
        organization_name: Union[str, Organization],
        respo_model: Optional[BaseRespoModel] = None,
        validate_input: bool = config.RESPO_CHECK_FORCE,
    ) -> bool:
        res = super().add_organization(organization_name, respo_model, validate_input)
        self.changed()
        return res

    def remove_organization(
        self,
        organization_name: Union[str, Organization],
        respo_model: Optional[BaseRespoModel] = None,
        validate_input: bool = config.RESPO_CHECK_FORCE,
    ) -> bool:
        res = super().remove_organization(
            organization_name, respo_model, validate_input
        )
        self.changed()
        return res

    def add_role(
        self,
        role_name: Union[str, Role],
        respo_model: Optional[BaseRespoModel] = None,
        validate_input: bool = config.RESPO_CHECK_FORCE,
    ) -> bool:
        res = super().add_role(role_name, respo_model, validate_input)
        self.changed()
        return res

    def remove_role(
        self,
        role_name: Union[str, Role],
        respo_model: Optional[BaseRespoModel] = None,
        validate_input: bool = config.RESPO_CHECK_FORCE,
    ) -> bool:
        res = super().remove_role(role_name, respo_model, validate_input)
        self.changed()
        return res


class ColumnMixRespoField(Column, MutableRespoClient):
    pass


def get_empty_respo_field():
    return MutableRespoClient()


SQLAlchemyRespoField: ColumnMixRespoField = Column(
    MutableRespoClient.as_mutable(TEXTRespoField),  # type: ignore
    nullable=False,
    server_default="",
    default=get_empty_respo_field,
)
