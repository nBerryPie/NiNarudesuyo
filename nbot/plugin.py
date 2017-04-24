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
        self.__command_tasks = {}
        self.__loading_module_name = None

    @property
    def commands(self) -> List[str]:
        return list(self.__command_tasks.keys())

    def get_schedule_tasks(self, hour: int, minute: int) -> List[Tuple[str, Callable[[str], None]]]:
        return self.__schedule_tasks[hour][minute]

    def get_command_task(self, command: str) -> Optional[Tuple[str, Callable[[str, List[str]], None]]]:
        return self.__command_tasks[command] if command in self.__command_tasks else None

    def load_plugins(self) -> None:
        for file_name in listdir(self.plugins_dir):
            if file_name.endswith(".py"):
                m = import_module(".".join([self.plugins_dir, file_name[:-3]]))
                self.__plugins.append(m)
                self.__logger.info("Load Module: {}".format(m.__name__))

    @staticmethod
    def __get_function_name(func: Callable[[], None]):
        return '.'.join([getargvalues(stack()[3].frame).locals['__name__'], func.__name__])

    def add_schedule_task(self, hour: int, minute: int, task: Callable[[str], None]) -> None:
        self.__schedule_tasks[hour][minute].append((self.__get_function_name(task), task))

    def add_command_task(self, command: str, task: Callable[[str, List[str]], None]) -> None:
        self.__command_tasks[command] = (self.__get_function_name(task), task)
