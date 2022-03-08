from typing import Optional
from sqlalchemy.types import TEXT, TypeDecorator

from respo.client import RespoClient
from respo.respo_model import RespoModel
from sqlalchemy.ext.mutable import Mutable
from sqlalchemy import Column


class TEXTRespoField(TypeDecorator):
    """Platform-independent Custom Type to store Respo model based on TEXT type"""

    class TEXTRespo(TEXT):
        @property
        def python_type(self):
            return MutableRespoClient

    impl = TEXTRespo
    cache_ok = True

    def process_bind_param(
        self, value: Optional[RespoClient], dialect
    ) -> Optional[str]:
        if value is None:
            return value
        return str(value)

    def process_result_value(
        self, value: Optional[str], dialect
    ) -> Optional["MutableRespoClient"]:
        if value is None:
            return value
        return MutableRespoClient(json_string=value)


class MutableRespoClient(Mutable, RespoClient):
    @classmethod
    def coerce(cls, key, value):
        if isinstance(value, cls):
            return value
        return MutableRespoClient.coerce(key, value)

    def add_organization(
        self,
        organization_name: str,
        respo_model: RespoModel,
        validate_input: bool = True,
    ):
        super().add_organization(organization_name, respo_model, validate_input)
        self.changed()

    def add_role(
        self, role_name: str, respo_model: RespoModel, validate_input: bool = True
    ):
        super().add_role(role_name, respo_model, validate_input)
        self.changed()


class ColumnMixRespoField(Column, MutableRespoClient):
    pass


RespoField: ColumnMixRespoField = Column(
    MutableRespoClient.as_mutable(TEXTRespoField), nullable=False, server_default=""  # type: ignore
)
