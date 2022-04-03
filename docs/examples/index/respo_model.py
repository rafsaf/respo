"""
Auto generated using respo create command
Docs: https://rafsaf.github.io/respo/
"""

import typing

import respo


class RespoModel(respo.RespoModel):
    if typing.TYPE_CHECKING:

        class _ROLES(respo.ROLESContainer):
            ADMIN: str
            DEFAULT: str

        class _PERMS(respo.PERMSContainer):
            USER__ALL: str
            USER__READ_ALL: str
            USER__READ_BASIC: str

        PERMS: _PERMS
        ROLES: _ROLES

        @staticmethod
        def get_respo_model() -> "RespoModel":
            return respo.RespoModel.get_respo_model()  # type: ignore
