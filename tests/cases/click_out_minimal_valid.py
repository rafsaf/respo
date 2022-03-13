"""
Auto generated using respo create command
Docs: https://rafsaf.github.io/respo/
"""

import respo
import typing


class RespoModel(respo.RespoModel):
    if typing.TYPE_CHECKING:

        class ROLES:
            pass

        class PERMS:
            pass

        @staticmethod
        def get_respo_model() -> "RespoModel":
            return respo.RespoModel.get_respo_model()  # type: ignore
