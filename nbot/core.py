# coding: utf-8
from datetime import datetime
from functools import wraps
from threading import Thread, current_thread
from time import sleep
from tweepy import API, OAuthHandler


from nbot.config import ConfigManager
from nbot.plugin import PluginManager
from nbot.utils import initialize_logger


class __NBot(object):

    def __init__(self):
        self.config_manager = ConfigManager()
        initialize_logger(self.config_manager.logs_dir)
        self.__accounts = {}
        self.plugin_manager = PluginManager(self.config_manager.plugins_dir)

    def run(self):
        self.plugin_manager.load_plugins()
        Thread(target=self.__schedule_task, name="ScheduleTask", daemon=current_thread()).start()
        try:
            while True:
                pass
        except:
            pass

    def get_account(self, name: str) -> API:
        if name in self.__accounts:
            return self.__accounts[name]
        else:
            account = self.config_manager.accounts[name]
            app = self.config_manager.apps[account["app"]]
            auth = OAuthHandler(app["consumer_key"], app["consumer_token"])
            auth.set_access_token(account["access_token"], account["access_token_secret"])
            api = API(auth)
            self.__accounts[name] = api
            return api

    def __schedule_task(self):
        sleep(60 - datetime.now().second)
        while True:
            now = datetime.now()
            l = self.plugin_manager.get_schedule_tasks(now.hour, now.minute)
            for module_name, task in l:
                task(module_name)
            sleep(60 - datetime.now().second)

    def schedule_task(self, hours=list([h for h in range(24)]), minutes=list([0])):

        def f(func):

            @wraps(func)
            def decorated_func(module_name: str):
                Thread(target=func, name=".".join([module_name, func.__name__]), daemon=current_thread()).start()

            for hour in hours:
                for minute in minutes:
                    self.plugin_manager.add_schedule_task(hour, minute, decorated_func)
            return decorated_func

        return f

bot = __NBot()
