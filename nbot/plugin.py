# coding: utf-8
from datetime import datetime
from importlib import import_module
from logging import getLogger, Logger
from os import scandir
from typing import Callable, Dict, List, Optional


class PluginManager(object):

    class ScheduleTask(object):
        def __init__(self, hours: List[int], minutes: List[int], task: Callable[[], None]):
            self.hours: List[int] = hours
            self.minutes: List[int] = minutes
            self.task: Callable[[], None] = task

        def __call__(self, now: datetime):
            if now.hour in self.hours and now.minute in self.minutes:
                self.task()

    __logger: Logger = getLogger(__name__)
    __plugins: List[object] = []
    __schedule_tasks: Dict[str, ScheduleTask] = {}
    __command_tasks: Dict[str, Callable[[List[str]], None]] = {}
    __commands: Dict[str, str] = {}

    def __init__(self, plugins_dir: str):
        self.__plugins_dir: str = plugins_dir

    def get_schedule_tasks(self) -> List[ScheduleTask]:
        return list(self.__schedule_tasks.values())

    def get_schedule_task(self, task_name: str) -> Optional[Callable[[], None]]:
        print(self.__schedule_tasks)
        print(task_name)
        if task_name in self.__schedule_tasks.keys():
            return self.__schedule_tasks[task_name]
        else:
            return None

    @property
    def commands(self) -> List[str]:
        return list(self.__commands.keys())

    def get_command_task(self, command: str) -> Optional[Callable[[List[str]], None]]:
        if command in self.__commands:
            task_name = self.__commands[command]
            if task_name in self.__command_tasks:
                return self.__command_tasks[task_name]
        return None

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
        self.__logger.info(f"Load Module: {m.__name__}")

    def add_schedule_task(self, hours: List[int], minutes: List[int], task: Callable[[], None], task_name: str) -> None:
        self.__schedule_tasks[task_name] = (self.ScheduleTask(hours, minutes, task))

    def add_command_task(self, command: str, task: Callable[[List[str]], None], task_name: str) -> None:
        self.__command_tasks[task_name] = task
        self.__commands[command] = task_name
