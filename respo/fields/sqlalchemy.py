from typing import Optional
from sqlalchemy.types import TEXT, TypeDecorator

from respo.client import RespoClient


class RespoField(TypeDecorator):
    """Platform-independent RespoClient Field based on TEXT type"""

    class RespoTEXT(TEXT):
        @property
        def python_type(self):
            return RespoClient

    impl = RespoTEXT
    cache_ok = False

    def process_bind_param(
        self, value: Optional[RespoClient], dialect
    ) -> Optional[str]:
        if value is None:
            return value
        import logging

        logging.error("process_bind_param")
        logging.error(value)
        logging.error(str(value))
        return str(value)

    def process_result_value(
        self, value: Optional[str], dialect
    ) -> Optional[RespoClient]:
        if value is None:
            return value
        import logging

        logging.error("process_result_value")
        logging.error(value)
        return RespoClient(json_string=value)
