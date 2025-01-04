from contextvars import ContextVar

DB_DATE_FORMAT = "%y-%m-%d %H:%M:%S"

correlation_id = ContextVar("correlation_id", default="-")
