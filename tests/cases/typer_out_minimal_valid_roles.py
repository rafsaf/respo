"""
Auto generated using respo create command
Docs: https://rafsaf.github.io/respo/
"""

from respo import BaseRespoModel, Organization, Role


class RespoModel(BaseRespoModel):
    class ORGS:
        DEFAULT: Organization

    class ROLES:
        DEFAULT__ROOT: Role
        DEFAULT__USER: Role

    class PERMS:
        pass

    @staticmethod
    def get_respo_model() -> "RespoModel":
        return BaseRespoModel.get_respo_model()  # type: ignore
