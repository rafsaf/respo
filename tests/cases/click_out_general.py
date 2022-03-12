"""
Auto generated using respo create command
Docs: https://rafsaf.github.io/respo/
"""

from respo import Organization, RespoModel, Role


class RespoModel(RespoModel):
    class ORGS:
        BOOK123: Organization
        DEFAULT: Organization
        DEFAULT_DENY: Organization
        TEST_O: Organization

    class ROLES:
        BOOK123__ADMIN_ROLE: Role
        BOOK123__CLIENT: Role
        BOOK123__ROOT: Role
        BOOK123__SUPERUSER_BOOK: Role
        DEFAULT_DENY__ROOT: Role
        DEFAULT__ROOT: Role
        DEFAULT__SUPERUSER: Role
        DEFAULT__TEST_ROLE: Role
        TEST_O__ROOT: Role

    class PERMS:
        BOOK123__BOOK__BUY: str
        BOOK123__BOOK__BUY_ALL: str
        BOOK123__BOOK__LIST: str
        BOOK123__BOOK__READ: str
        BOOK123__USER__READ_BASIC: str
        DEFAULT__USER__READ_ALL: str
        DEFAULT__USER__READ_ALL_BETTER: str
        DEFAULT__USER__READ_BASIC: str
        TEST_O__TEST__A: str
        TEST_O__TEST__B: str
        TEST_O__TEST__C: str
        TEST_O__TEST__D: str
        TEST_O__TEST__E: str
        TEST_O__TEST__F: str
