# coding: utf-8
from datetime import datetime
from functools import wraps
import json
from threading import Thread, current_thread
from time import sleep
from tweepy import API, OAuthHandler

from nbot.constant import *
from nbot.plugin import PluginManager
from nbot.utils import initialize_logger


class __NBot(object):

    def __init__(self):
        initialize_logger(LOG_DIR)
        self.__apis = {}
        with open("config.json", "r") as f:
            config = json.loads(f.read())
            self.__apps = config["apps"]
            self.__accounts = config["accounts"]
            self.plugin_manager = PluginManager()

    def run(self):
        self.plugin_manager.load_plugins()
        Thread(target=self.__schedule_task, name="ScheduleTask", daemon=current_thread()).start()
        try:
            while True:
                pass
        except:
            pass

    def get_account(self, name: str) -> API:
        if name in self.__apis:
            return self.__apis[name]
        else:
            account = self.__accounts[name]
            app = self.__apps[account["app"]]
            auth = OAuthHandler(app["consumer_key"], app["consumer_token"])
            auth.set_access_token(account["access_token"], account["access_token_secret"])
            api = API(auth)
            self.__apis[name] = api
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
