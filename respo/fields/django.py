from typing import Optional

from django.db.models import TextField

from respo.client import RespoClient


class DjangoRespoField(TextField, RespoClient):
    """
    Django field that represent `respo.RespoClient` instance, based on TextField.

    It is serialized and deserialized from `str` to `respo.RespoClient` and reverse back and forth
    when writing and reading it from database. It *should* be updated in-place by calling methods.

    ### Example usage
    ```
    from django.db import models
    from respo.fields.django import DjangoRespoField

    class TheModel(models.Model):
        respo_field = DjangoRespoField(default="", null=False)

    ```
    If for some reason typing help for `respo_field` is Unknown, you can use following hack
    ```
    # imports like above plus typing.TYPE_CHECKING

    class TheModel(models.Model):
        respo_field = DjangoRespoField(default="", null=False)  # type: ignore

        if TYPE_CHECKING:
            @property
            def respo_field(self) -> DjangoRespoField:
                ...
    ```

    """

    def from_db_value(self, value: Optional[str], expression, connection):
        return RespoClient(value)

    def to_python(self, value):  # pragma: no cover
        if isinstance(value, RespoClient):
            return value
        return RespoClient(value)

    def get_prep_value(self, value: RespoClient):
        return str(value)
