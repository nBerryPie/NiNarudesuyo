import json
from typing import Any


class ConfigManager(object):

    def __init__(self):
        self.__config = {}
        self.__load_config()

    def __load_config(self):
        with open("config.json", "r") as f:
            self.__config = json.loads(f.read())

    def reload_config(self):
        self.__load_config()

    def get_config_value(self, path: str, default: Any=None):
        l = path.split(".")

        def f(d):
            s = l.pop(0)
            if isinstance(d, dict) and s in d:
                if len(l) == 0:
                    return d[s]
                else:
                    return f(d[s])
            else:
                return default

        return f(self.__config)
