from datetime import datetime
from logging import getLogger, Formatter, StreamHandler, INFO, DEBUG
from logging.handlers import RotatingFileHandler
from os import makedirs, path


def initialize_logger(log_dir: str) -> None:
    path.exists(log_dir) or makedirs(log_dir)
    logger = getLogger()
    formatter = Formatter("[%(asctime)s][%(threadName)s %(name)s/%(levelname)s]: %(message)s")
    stream_handler = StreamHandler()
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(INFO)
    logger.addHandler(stream_handler)
    file_name = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".log"
    file_handler = RotatingFileHandler("/".join([log_dir, file_name]), encoding='utf-8')
    file_handler.setFormatter(formatter)
    file_handler.setLevel(DEBUG)
    logger.addHandler(file_handler)
    logger.setLevel(DEBUG)
    getLogger("tweepy").setLevel(100)
