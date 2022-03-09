from typing import Optional

from django.db.models import TextField

from respo.client import RespoClient


class DjangoRespoField(TextField, RespoClient):
    def from_db_value(self, value: Optional[str], expression, connection):
        return RespoClient(value)

    def to_python(self, value):  # pragma: no cover
        if isinstance(value, RespoClient):
            return value
        return RespoClient(value)

    def get_prep_value(self, value: RespoClient):
        return str(value)
