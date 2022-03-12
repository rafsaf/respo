"""
Auto generated using respo create command
Docs: https://rafsaf.github.io/respo/
"""

import respo


class RespoModel(respo.RespoModel):
    class ORGS:
        DEFAULT: respo.Organization

    class ROLES:
        DEFAULT__ROOT: respo.Role
        DEFAULT__USER: respo.Role

    class PERMS:
        pass

    @staticmethod
    def get_respo_model() -> "RespoModel":
        return respo.RespoModel.get_respo_model()  # type: ignore