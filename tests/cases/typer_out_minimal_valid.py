"""
Auto generated using respo create command
Docs: https://rafsaf.github.io/respo/
"""

from respo import BaseRespoModel


class RespoModel(BaseRespoModel):
    class ORGS:
        pass

    class ROLES:
        pass

    class PERMS:
        pass

    @staticmethod
    def get_respo_model() -> "RespoModel":
        return BaseRespoModel.get_respo_model()  # type: ignore
