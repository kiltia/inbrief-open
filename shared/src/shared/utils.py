import re
import string

import numpy as np
from numpy.linalg import norm

from .patterns import emoji_pattern

DATE_FORMAT = "%d/%m/%y %H:%M:%S"
DB_DATE_FORMAT = "%y-%m-%d %H:%M:%S"
DEFAULT_END_DATE = "01/01/01 00:00:00"
CACHE_PATH = "cache"
SHARED_CONFIG_PATH = "../shared/config"
REQUEST_ID_HEADER = "X-Request-Id"


def cos_sim(embedding1, embedding2):
    return np.dot(embedding1, embedding2) / (norm(embedding1) * norm(embedding2))


def get_class_score(embedding1, embedding2, scorer=cos_sim):
    return scorer(np.array(embedding1), np.array(embedding2))


def clean_text(text, remove_punctuation=False):
    text = re.sub(
        r"https?:\/\/.*[\r\n]*",
        "",
        emoji_pattern.sub(r"", text),
        flags=re.MULTILINE,
    )
    text = re.sub(r"@.*[\r\n]*", "", text, flags=re.MULTILINE)
    text = re.sub(r"#.*[\r\n]*", "", text, flags=re.MULTILINE)
    text = re.sub("[\[(\])]", "", text)
    if remove_punctuation:
        text = text.translate(str.maketrans("", "", string.punctuation + "«»" + "—"))
    return text
