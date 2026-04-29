import logging
import sys
from uuid import uuid4


class RequestIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        if not hasattr(record, "request_id"):
            record.request_id = "external"
        return True


def configure_logging() -> None:
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    root_logger.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    handler.addFilter(RequestIdFilter())

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | request_id=%(request_id)s | %(message)s"
    )

    handler.setFormatter(formatter)
    root_logger.addHandler(handler)

    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)


def new_request_id() -> str:
    return str(uuid4())


class RequestIdAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        extra = kwargs.setdefault("extra", {})
        extra.setdefault("request_id", self.extra.get("request_id", "unknown"))
        return msg, kwargs


def get_logger(name: str, request_id: str = "system") -> RequestIdAdapter:
    return RequestIdAdapter(
        logging.getLogger(name),
        {"request_id": request_id},
    )