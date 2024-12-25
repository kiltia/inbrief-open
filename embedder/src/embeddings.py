import logging

import torch
from rb_tocase import Case
from transformers import AutoModel

logger = logging.getLogger("embedder")


class EmbeddingProvider:
    @classmethod
    def get_label(self):
        return Case.to_kebab(self.__name__).removesuffix("-embedder")


class JinaEmbedder(EmbeddingProvider):
    MODEL_NAME = "jinaai/jina-embeddings-v3"

    def __init__(self, device: torch.device) -> None:
        self.model = AutoModel.from_pretrained(
            self.MODEL_NAME, trust_remote_code=True
        )
        self.device = device
        self.model.to(device)

    def get_embeddings(self, inputs: list, **kwargs):
        results = []
        for input in inputs:
            embedding = self.model.encode(input)

            results.append(embedding)
        return results


def init_embedders(
    required_embedders: list[str], device: torch.device
) -> list[EmbeddingProvider]:
    embedders = []

    candidates = EmbeddingProvider.__subclasses__()
    for embedder in candidates:
        print(embedder.get_label())
        if embedder.get_label() not in required_embedders:
            continue

        logger.info(f"Started loading {embedder.get_label()}")
        try:
            obj = embedder(device)
            embedders.append(obj)
        except Exception as e:
            logging.error(
                f"Got {type(e).__name__} exception while initializing {embedder.get_label()}: {e}"
            )
        logger.info(f"Finished loading {embedder.get_label()}")
    return embedders
