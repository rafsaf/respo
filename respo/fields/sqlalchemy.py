from sqlalchemy.types import TypeDecorator, TEXT
from respo.client import RespoClient


class RespoField(TypeDecorator):
    """Platform-independent RespoClient Field based on TEXT type"""

    impl = TEXT
    cache_ok = True

    def process_bind_param(self, value: RespoClient, dialect) -> str:
        return str(value)

    def process_result_value(self, value: str, dialect) -> RespoClient:
        return RespoClient(json_string=value)
