import logging

from utils import correlation_id

logger = logging.getLogger("scraper")


class CorrelationIdFilter(logging.Filter):
    def filter(self, record):
        try:
            record.correlation_id = str(correlation_id.get())
        except LookupError:
            record.correlation_id = "-"
        return True
