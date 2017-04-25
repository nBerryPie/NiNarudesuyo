# coding: utf-8
from importlib import import_module
from logging import getLogger, Logger
from os import scandir
from typing import Callable, Dict, List, Optional


class PluginManager(object):

    __logger: Logger = getLogger(__name__)
    __plugins: List[object] = []
    __schedule_tasks: List[List[List[Callable[[str], None]]]] = [[[] for m in range(60)] for h in range(24)]
    __command_tasks: Dict[str, Callable[[str, List[str]], None]] = {}

    def __init__(self, plugins_dir: str):
        self.__plugins_dir: str = plugins_dir

    @property
    def commands(self) -> List[str]:
        return list(self.__command_tasks.keys())

    def get_schedule_tasks(self, hour: int, minute: int) -> List[Callable[[str], None]]:
        return self.__schedule_tasks[hour][minute]

    def get_command_task(self, command: str) -> Optional[Callable[[str, List[str]], None]]:
        return self.__command_tasks[command] if command in self.__command_tasks else None

    def load_plugins(self) -> None:
        with scandir(self.__plugins_dir) as d:
            [
                self.__load_plugin(entry.path[:-3].replace('/', '.'))
                for entry in d
                if entry.is_file() and entry.name.endswith(".py")
            ]

    def __load_plugin(self, name: str) -> None:
        m = import_module(name)
        self.__plugins.append(m)
        self.__logger.info("Load Module: {}".format(m.__name__))

    def add_schedule_task(self, hour: int, minute: int, task: Callable[[], None]) -> None:
        self.__schedule_tasks[hour][minute].append(task)

    def add_command_task(self, command: str, task: Callable[[List[str]], None]) -> None:
        self.__command_tasks[command] = task
        print(dir(task))
        print(dir(task.__closure__))
        print(dir(task.__closure__[1]))
        print(task.__closure__[1].cell_contents)
