"""
Auto generated using respo create command
Docs: https://rafsaf.github.io/respo/
"""

from respo import Organization, RespoModel, Role


class RespoModel(RespoModel):
    class ORGS:
        DEFAULT: Organization

    class ROLES:
        DEFAULT__ROOT: Role
        DEFAULT__USER: Role

    class PERMS:
        pass
