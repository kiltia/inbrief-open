from contextvars import ContextVar

SOCIAL_FEATURES = ["comments", "reactions"]
SESSION_PATH = "sessions"
DB_DATE_FORMAT = "%y-%m-%d %H:%M:%S"

correlation_id = ContextVar("correlation_id")
