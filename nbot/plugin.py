# coding: utf-8
from importlib import import_module
from inspect import stack, getargvalues
from logging import getLogger
from os import listdir
from typing import Callable, List, Optional, Tuple


class PluginManager(object):

    def __init__(self, plugins_dir: str):
        self.__logger = getLogger(__name__)
        self.plugins_dir = plugins_dir
        self.__plugins = []
        self.__schedule_tasks = [[[] for m in range(60)] for h in range(24)]
        self.__loading_module_name = None

    @property
    def plugins(self):
        return list(self.__plugins)

    def get_schedule_tasks(self, hour: int, minute: int) -> List[Tuple[str, Callable[[str], None]]]:
        return self.__schedule_tasks[hour][minute]


    def load_plugins(self) -> None:
        for file_name in listdir(self.plugins_dir):
            if file_name.endswith(".py"):
                m = import_module(".".join([self.plugins_dir, file_name[:-3]]))
                self.__plugins.append(m)
                self.__logger.info("Load Module: {}".format(m.__name__))

    def add_schedule_task(self, hour: int, minute: int, task: Callable[[str], None]) -> None:
        self.__schedule_tasks[hour][minute].append((getargvalues(stack()[2].frame).locals['__name__'], task))

