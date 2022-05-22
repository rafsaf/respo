"""
Auto generated using respo create command
Docs: https://rafsaf.github.io/respo/
"""

import typing

import respo


class RespoModel(respo.RespoModel):
    if typing.TYPE_CHECKING:

        class _ROLES(respo.ROLESContainer):
            pass

        class _PERMS(respo.PERMSContainer):
            pass

        PERMS: _PERMS
        ROLES: _ROLES

        @staticmethod
        def get_respo_model() -> "RespoModel":
            return respo.RespoModel.get_respo_model()  # type: ignore
