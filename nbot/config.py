import json


class ConfigManager(object):

    def __init__(self):
        self.apps = {}
        self.accounts = {}
        self.logs_dir = ""
        self.plugins_dir = ""
        self.__load_config()

    def __load_config(self):
        with open("config.json", "r") as f:
            root = json.loads(f.read())
            self.apps = root["apps"]
            self.accounts = root["accounts"]
            if "directory" in root:
                directory = root["directory"]
                self.logs_dir = directory["logs"] if "logs" in directory else "logs"
                self.plugins_dir = directory["plugins"] if "plugins" in directory else "plugins"
            else:
                self.logs_dir = "logs"
                self.plugins_dir = "plugins"

    def reload_config(self):
        self.__load_config()
