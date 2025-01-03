import logging

from context import correlation_id

logger = logging.getLogger("scraper")


class CorrelationIdFilter(logging.Filter):
    def filter(self, record):
        record.correlation_id = correlation_id.get()
        return True
