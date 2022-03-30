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
            PRO_USER: str
            SUPERADMIN: str

        class PERMS:
            BOOK__ALL: str
            BOOK__BUY: str
            BOOK__LIST: str
            BOOK__READ: str
            BOOK__SELL: str
            USER__ALL: str
            USER__READ_ALL: str
            USER__READ_ALL_BETTER: str
            USER__READ_BASIC: str
            USER__UPDATE: str

        @staticmethod
        def get_respo_model() -> "RespoModel":
            return respo.RespoModel.get_respo_model()  # type: ignore
