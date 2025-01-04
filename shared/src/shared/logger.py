import json
import logging
from logging.config import dictConfig

from shared.utils import SHARED_CONFIG_PATH, correlation_id


def configure_logging(override_path=None) -> None:
    if override_path is not None:
        path = override_path
    else:
        path = f"{SHARED_CONFIG_PATH}/settings.json"
    with open(path) as f:
        d = json.load(f)
        dictConfig(d["logger"])


class CorrelationIdFilter(logging.Filter):
    def filter(self, record):
        try:
            record.correlation_id = str(correlation_id.get())
        except LookupError:
            record.correlation_id = "-"
        return True
