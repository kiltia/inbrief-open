import logging

import redis
from rb_tocase import Case

from config import ProviderConfig

logger = logging.getLogger("embedder")


class BaseProvider:
    def __init__(self, *args) -> None:
        pass

    @classmethod
    def get_label(cls):
        return Case.to_kebab(self.__name__).removesuffix("-provider")  # pyright:ignore

    def get(self, request_id) -> bytes:
        raise NotImplementedError


def init_providers(config: ProviderConfig) -> list[BaseProvider]:
    required_providers = config.required_providers
    candidates = BaseProvider.__subclasses__()
    logger.info(f"Required providers: {required_providers}")
    providers = []
    for exporter in candidates:
        if exporter.get_label() not in required_providers:
            continue
        logger.info(f"Started loading {exporter.get_label()}")
        try:
            obj = exporter(config)
            providers.append(obj)
        except Exception as e:
            logger.error(
                f"Got {type(e).__name__} exception while initializing {exporter.get_label()}: {e}"
            )
            continue

        logger.info(f"Finished loading {exporter.get_label()}")
    return providers


class RedisProvider(BaseProvider):
    def __init__(self, config: ProviderConfig):
        self.client = redis.Redis(
            config.redis.host, config.redis.port, db=0, protocol=3
        )

    def set(self, request_id, json_dump):
        self.client.set(
            str(request_id),
            json_dump,
        )

    def get(self, request_id) -> bytes:
        return self.client.get(str(request_id))  # pyright:ignore
