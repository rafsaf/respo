"""
Auto generated using respo create command
Docs: https://rafsaf.github.io/respo/
"""

import respo


class RespoModel(respo.RespoModel):
    class ORGS:
        BOOK123: respo.Organization
        DEFAULT: respo.Organization
        DEFAULT_DENY: respo.Organization
        TEST_O: respo.Organization

    class ROLES:
        BOOK123__ADMIN_ROLE: respo.Role
        BOOK123__CLIENT: respo.Role
        BOOK123__ROOT: respo.Role
        BOOK123__SUPERUSER_BOOK: respo.Role
        DEFAULT_DENY__ROOT: respo.Role
        DEFAULT__ROOT: respo.Role
        DEFAULT__SUPERUSER: respo.Role
        DEFAULT__TEST_ROLE: respo.Role
        TEST_O__ROOT: respo.Role

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
