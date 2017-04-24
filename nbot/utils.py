from datetime import datetime
from logging import getLogger, Formatter, StreamHandler, INFO, DEBUG
from logging.handlers import RotatingFileHandler
from os import makedirs, path
from threading import Thread, current_thread
from typing import Callable, Tuple


def initialize_logger(logs_dir: str, plugins_dir: str) -> None:
    path.exists(logs_dir) or makedirs(logs_dir)
    logger = getLogger()
    formatter = Formatter("[%(asctime)s][%(name)s/%(levelname)s]: %(message)s")
    stream_handler = StreamHandler()
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(INFO)
    logger.addHandler(stream_handler)
    file_name = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".log"
    file_handler = RotatingFileHandler("/".join([logs_dir, file_name]), encoding='utf-8')
    file_handler.setFormatter(formatter)
    file_handler.setLevel(DEBUG)
    logger.addHandler(file_handler)
    getLogger("nbot").setLevel(DEBUG)
    getLogger(plugins_dir).setLevel(DEBUG)


def create_thread(target: Callable[[], None], module_name: str, args: Tuple=()) -> Thread:
    return Thread(target=target, name=".".join([module_name, target.__name__]), args=args, daemon=current_thread())