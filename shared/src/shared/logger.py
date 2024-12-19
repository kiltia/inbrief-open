import json
import logging
from logging.config import dictConfig

from .utils import SHARED_CONFIG_PATH

test = "123"

def configure_logging(override_path=None) -> None:
    from functools import partial, partialmethod

    if override_path is not None:
        path = override_path
    else:
        path = f"{SHARED_CONFIG_PATH}/settings.json"
    with open(path) as f:
        d = json.load(f)
        dictConfig(d["logger"])

    logging.TRACE = logging.DEBUG - 5
    logging.addLevelName(logging.TRACE, "TRACE")
    logging.Logger.trace = partialmethod(logging.Logger.log, logging.TRACE)
    logging.trace = partial(logging.log, logging.TRACE)
