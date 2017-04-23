# coding: utf-8
from collections import defaultdict
from functools import wraps
from importlib import import_module
from logging import getLogger
from os import listdir
from threading import Thread
from typing import Callable, List

from nbot.constant import *


schedule_tasks = defaultdict(lambda: defaultdict(list))


def schedule_task(hours=list([h for h in range(24)]), minutes=list([0])):

    def f(func):

        @wraps(func)
        def decorated_func(bot):
            Thread(target=func, name=func.__name__, args=(bot,)).start()

        for hour in hours:
            for minute in minutes:
                schedule_tasks[hour][minute].append(decorated_func)
        return decorated_func
    return f


class PluginManager(object):

    def __init__(self):
        self.__logger = getLogger(__name__)
        self.__plugins = []
        self.__schedule_tasks = {}
        self.load_plugins()

    @property
    def plugins(self):
        return list(self.__plugins)

    def get_schedule_tasks(self, hour, minute) -> List:
        return self.__schedule_tasks[hour][minute]

    def load_plugins(self):
        for file_name in listdir(PLUGINS_DIR):
            if file_name.endswith(".py"):
                m = import_module(".".join([PLUGINS_DIR, file_name[:-3]]))
                self.__plugins.append(m)
                self.__logger.info("Load: {}".format(file_name))
        self.__schedule_tasks = schedule_tasks
