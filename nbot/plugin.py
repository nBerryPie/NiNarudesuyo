# coding: utf-8
from importlib import import_module
from os import listdir

from nbot.constant import *


class PluginManager(object):

    def __init__(self, logger):
        self.__logger = logger
        self.__plugins = []
        self.load_plugins()

    @property
    def plugins(self):
        return list(self.__plugins)

    def load_plugins(self):
        for file_name in listdir(PLUGINS_DIR):
            if file_name.endswith(".py"):
                m = import_module(".".join([PLUGINS_DIR, file_name[:-3]]))
                self.__plugins.append(m)
                self.__logger.info("Load: {}".format(file_name))

    def reload_plugins(self):
        self.__plugins = []
        self.load_plugins()
