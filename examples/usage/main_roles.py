# main.py

from .respo_model import RespoModel

RESPO_MODEL = RespoModel.get_respo_model()

print(RESPO_MODEL.ROLES)
# {'default': ['user.read_basic'], 'admin': ['user.read_all', 'user.read_basic']}

print(RESPO_MODEL.ROLES.DEFAULT)
# default

print("test_role" in RESPO_MODEL.PERMS)
# False
