# coding: utf-8
from cmd import Cmd
from datetime import datetime
from functools import wraps
from inspect import stack, getargvalues
from logging import getLogger, Logger
from threading import Thread, current_thread
from time import sleep
from typing import Callable, Dict, List, Optional
from tweepy import API, OAuthHandler

from nbot.config import ConfigManager
from nbot.plugin import PluginManager
from nbot.utils import initialize_logger, create_thread


class NBot(object):

    config_manager: ConfigManager = ConfigManager()
    __logger: Logger = getLogger(__name__)
    __apis: Dict[str, API] = {}
    __accounts: dict = config_manager.get_config_value("accounts", {})
    __apps: dict = config_manager.get_config_value("apps", {})
    plugin_manager: PluginManager = PluginManager(config_manager.get_config_value("directory.plugins", "plugins"))

    def __init__(self) -> None:
        initialize_logger(
            self.config_manager.get_config_value("directory.logs", "logs"),
            self.config_manager.get_config_value("directory.plugins", "plugins")
        )

    def run(self) -> None:
        import nbot.command
        self.plugin_manager.load_plugins()
        Thread(target=self.__schedule_task, name="ScheduleTask", daemon=current_thread()).start()
        try:
            self.__command_task()
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
            for task in self.plugin_manager.get_schedule_tasks():
                task(now)
            sleep(60 - datetime.now().second)

    def __command_task(self) -> None:

        class Command(Cmd):
            prompt: str = "> "

            def __init__(self, bot: NBot):
                super().__init__()
                self.bot = bot

            def __getattr__(self, item: str):
                if item.startswith("do_"):
                    command = item[3:]
                    task = self.bot.plugin_manager.get_command_task(command)
                    if task is None:
                        return lambda args: print("Unknown Command.")
                    else:
                        return lambda args: task(args.split(' '))

                elif item.startswith("help_"):
                    # ToDo: helpの処理を書く
                    raise AttributeError
                raise AttributeError

            def complete(self, text: str, state: int):
                commands = [s for s in self.bot.plugin_manager.commands if s.startswith(text)]
                if len(commands) <= state:
                    return None
                else:
                    return commands[state]

        Command(self).cmdloop()

    def schedule_task(
            self,
            name: str=None,
            hours: List[int]=list([h for h in range(24)]),
            minutes: List[int]=list([0])
    ) -> Callable[[Callable[[], None]], Callable[[], None]]:

        def f(func: Callable[[], None]) -> Callable[[str], None]:
            if name:
                task_name = name
            else:
                task_name = '_'.join([getargvalues(stack()[1].frame).locals['__name__'].split(".")[1], func.__name__])

            @wraps(func)
            def decorated_func() -> None:
                create_thread(func, task_name).start()

            self.plugin_manager.add_schedule_task(hours, minutes, decorated_func, task_name)
            return decorated_func

        return f

    def command_task(
            self,
            command: str,
            name: str=None
    ) -> Callable[[Callable[[List[str]], None]], Callable[[List[str]], None]]:

        def f(func: Callable[[List[str]], None]) -> Callable[[List[str]], None]:
            if name:
                task_name = name
            else:
                task_name = '_'.join([getargvalues(stack()[1].frame).locals['__name__'].split(".")[1], func.__name__])

            @wraps(func)
            def decorated_func(args: List[str]) -> None:
                create_thread(func, task_name, (args,)).start()

            self.plugin_manager.add_command_task(command, decorated_func, task_name)
            return decorated_func

        return f
