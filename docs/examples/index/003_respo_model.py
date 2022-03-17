"""
Auto generated using respo create command
Docs: https://rafsaf.github.io/respo/
"""

import typing

import respo


class RespoModel(respo.RespoModel):
    if typing.TYPE_CHECKING:

        class ROLES:
            ADMIN: str
            DEFAULT: str

        class PERMS:
            USER__ALL: str
            USER__READ_ALL: str
            USER__READ_BASIC: str

        @staticmethod
        def get_respo_model() -> "RespoModel":
            return respo.RespoModel.get_respo_model()  # type: ignore
