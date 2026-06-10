import logging

LOG_FORMAT = "%(asctime)s | %(name)s | %(levelname)s | %(message)s"


def setup_logging(level: int = logging.INFO) -> None:
    root = logging.getLogger()
    if not root.handlers:
        logging.basicConfig(level=level, format=LOG_FORMAT)


setup_logging()
