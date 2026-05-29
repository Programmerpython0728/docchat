"""
Strukturalashgan logging.

Production'da JSON format, dev'da chiroyli readable format.
Har bir request uchun unique ID berib, request ni butun pipeline
bo'ylab kuzatib boriladi.
"""
import logging
import sys
from contextvars import ContextVar

# Request ID ni har bir request uchun saqlaydi (async safe)
request_id_var: ContextVar[str] = ContextVar("request_id", default="-")


class RequestIDFilter(logging.Filter):
    """Har bir log message ga request_id qo'shadi"""

    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_var.get()
        return True


def setup_logging(log_level: str = "INFO") -> None:
    """Logging ni sozlash. main.py da chaqiriladi."""
    log_format = (
        "%(asctime)s | %(levelname)-8s | %(request_id)s | "
        "%(name)s:%(lineno)d | %(message)s"
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(log_format))
    handler.addFilter(RequestIDFilter())

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(log_level)

    # Uchinchi tomon loglarni biroz tinchitamiz
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
