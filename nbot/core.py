# coding: utf-8
import asyncio
from datetime import datetime
import json
import logging
from logging.handlers import RotatingFileHandler
from os import makedirs, path
from tweepy import API, OAuthHandler

from nbot.constant import *
from nbot.plugin import PluginManager


class NBot(object):

    def __init__(self):
        self.logger = self.__get_logger()
        self.__apis = {}
        with open("config.json", "r") as f:
            config = json.loads(f.read())
            self.__apps = config["apps"]
            self.__accounts = config["accounts"]
        self.plugin_manager = PluginManager(self.logger)

    def run(self):
        loop = asyncio.get_event_loop()
        asyncio.ensure_future(self.__schedule_task())
        loop.run_forever()

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

    @staticmethod
    def __get_logger():
        path.exists(LOG_DIR) or makedirs(LOG_DIR)
        logger = logging.getLogger(__name__)
        formatter = logging.Formatter("[%(asctime)s][%(threadName)s %(name)s/%(levelname)s]: %(message)s")
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        stream_handler.setLevel(logging.INFO)
        logger.addHandler(stream_handler)
        file_name = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".log"
        file_handler = RotatingFileHandler("/".join([LOG_DIR, file_name]), encoding='utf-8')
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.DEBUG)
        logger.addHandler(file_handler)
        logger.setLevel(logging.DEBUG)
        return logger

    async def __schedule_task(self):
        await asyncio.sleep(60 - datetime.now().second)
        while True:
            for plugin in self.plugin_manager.plugins:
                if datetime.now().minute in plugin.EXECUTE_MINUTES:
                    plugin.execute(self)
            await asyncio.sleep(60 - datetime.now().second)
