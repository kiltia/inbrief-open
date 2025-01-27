import logging

import redis
from rb_tocase import Case

from config import ConnectorConfig

logger = logging.getLogger("embedder")


class BaseConnector:
    def __init__(self, *args) -> None:
        pass

    @classmethod
    def get_label(cls):
        return Case.to_kebab(cls.__name__).removesuffix("-connector")  # pyright:ignore

    def import_from(self, request_id) -> bytes:
        raise NotImplementedError

    def export(self, request_id, json_dump):
        raise NotImplementedError

    def delete(self, request_id):
        raise NotImplementedError


def init_connectors(config: ConnectorConfig) -> list[BaseConnector]:
    required_connectors = list(
        set([config.required_importer] + config.required_exporters)
    )
    candidates = BaseConnector.__subclasses__()
    logger.info(f"Required connectors: {required_connectors}")
    connectors = []
    for exporter in candidates:
        if exporter.get_label() not in required_connectors:
            continue
        logger.info(f"Started loading {exporter.get_label()} connector")
        try:
            obj = exporter(config)
            connectors.append(obj)
        except Exception as e:
            logger.error(
                f"Got {type(e).__name__} exception while initializing {exporter.get_label()}: {e}"
            )
            continue

        logger.info(f"Finished loading {exporter.get_label()}")
    return connectors


class RedisConnector(BaseConnector):
    def __init__(self, config: ConnectorConfig):
        self.client = redis.Redis(
            config.redis.host, config.redis.port, db=0, protocol=3
        )

    def export(self, request_id, json_dump):
        self.client.set(
            str(request_id),
            json_dump,
        )

    def import_from(self, request_id) -> bytes:
        return self.client.get(str(request_id))  # pyright:ignore

    def delete(self, request_id):
        self.client.delete(str(request_id))


class FileConnector(BaseConnector):
    def __init__(self, config: ConnectorConfig):
        from pathlib import Path

        self.path = config.json_config.path
        Path(config.json_config.path).mkdir(parents=True, exist_ok=True)

    def export(self, request_id, json_dump):
        with open(f"{self.path}/{request_id}.json", "w") as f:
            f.write(json_dump)


def get_connector(name: str, available: list[BaseConnector]) -> BaseConnector:
    for conn in available:
        if conn.get_label() == name:
            return conn
    raise ValueError(f"No importer found for input: {name}")
