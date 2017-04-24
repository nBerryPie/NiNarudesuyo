# coding: utf-8
from datetime import datetime
from functools import wraps
from logging import getLogger
from threading import Thread, current_thread
from time import sleep
from typing import Callable, List, Optional
from tweepy import API, OAuthHandler

from nbot.config import ConfigManager
from nbot.plugin import PluginManager
from nbot.utils import initialize_logger, create_thread


class __NBot(object):

    def __init__(self) -> None:
        self.config_manager = ConfigManager()
        initialize_logger(
            self.config_manager.get_config_value("directory.logs", "logs"),
            self.config_manager.get_config_value("directory.plugins", "plugins")
        )
        self.__logger = getLogger(__name__)
        self.__apis = {}
        self.__accounts = self.config_manager.get_config_value("accounts", {})
        self.__apps = self.config_manager.get_config_value("apps", {})
        self.plugin_manager = PluginManager(self.config_manager.get_config_value("directory.plugins", "plugins"))

    def run(self) -> None:
        import nbot.command
        self.plugin_manager.load_plugins()
        Thread(target=self.__schedule_task, name="ScheduleTask", daemon=current_thread()).start()
        Thread(target=self.__command_task, name="CommandTask", daemon=current_thread()).start()
        try:
            while True:
                pass
        except:
            pass

    def get_account(self, name: str) -> Optional[API]:
        if name in self.__apis:
            return self.__apis[name]
        else:
            if name in self.__accounts:
                account = self.__accounts[name]
                if account["app"] in self.__apps:
                    app = self.__apps[account["app"]]
                    auth = OAuthHandler(app["consumer_key"], app["consumer_token"])
                    auth.set_access_token(account["access_token"], account["access_token_secret"])
                    api = API(auth)
                    self.__apis[name] = api
                    return api
            return None

    def __schedule_task(self) -> None:
        sleep(60 - datetime.now().second)
        while True:
            now = datetime.now()
            l = self.plugin_manager.get_schedule_tasks(now.hour, now.minute)
            for module_name, task in l:
                self.__logger.debug("Function Call: {}()".format(module_name))
                task(module_name)
            sleep(60 - datetime.now().second)

    def __command_task(self) -> None:
        while True:
            l = input("> ").split(" ")
            command = l.pop(0)
            t = self.plugin_manager.get_command_task(command)
            if t is None:
                self.__logger.warning("Unknown Command.")
            else:
                self.__logger.debug("Function Call: {}()".format(t[0]))
                t[1](t[0], l)

    def schedule_task(self, hours: List[int]=list([h for h in range(24)]), minutes: List[int]=list([0])) \
            -> Callable[[Callable[[], None]], Callable[[str], None]]:

        def f(func: Callable[[], None]) -> Callable[[str], None]:

            @wraps(func)
            def decorated_func(module_name: str) -> None:
                create_thread(func, module_name).start()

            for hour in hours:
                for minute in minutes:
                    self.plugin_manager.add_schedule_task(hour, minute, decorated_func)
            return decorated_func

        return f

    def command_task(self, command: str) -> Callable[[Callable[[List[str]], None]], Callable[[str, List[str]], None]]:

        def f(func: Callable[[List[str]], None]) -> Callable[[str, List[str]], None]:

            @wraps(func)
            def decorated_func(module_name: str, args: List[str]) -> None:
                create_thread(func, module_name, (args,)).start()

            self.plugin_manager.add_command_task(command, decorated_func)
            return decorated_func

        return f

bot = __NBot()
