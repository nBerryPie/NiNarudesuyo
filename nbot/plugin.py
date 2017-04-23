# coding: utf-8
from importlib import import_module
from inspect import stack, getargvalues
from logging import getLogger
from os import listdir
from typing import List

from nbot.constant import *


class PluginManager(object):

    def __init__(self):
        self.__logger = getLogger(__name__)
        self.__plugins = []
        self.__schedule_tasks = [[[] for m in range(60)] for h in range(24)]
        self.__loading_module_name = None

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
                self.__logger.info("Load Module: {}".format(m.__name__))

    def add_schedule_task(self, hour, minute, task):
        self.__schedule_tasks[hour][minute].append((getargvalues(stack()[2].frame).locals['__name__'], task))

