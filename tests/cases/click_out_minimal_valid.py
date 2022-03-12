"""
Auto generated using respo create command
Docs: https://rafsaf.github.io/respo/
"""

import respo


class RespoModel(respo.RespoModel):
    class ORGS:
        pass

    class ROLES:
        pass

    class PERMS:
        pass

    @staticmethod
    def get_respo_model() -> "RespoModel":
        return respo.RespoModel.get_respo_model()  # type: ignore
