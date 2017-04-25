# coding: utf-8
from logging import getLogger
from pyknp import Jumanpp
import random
import tweepy

from nbot import bot

JUMANPP = Jumanpp()
logger = getLogger(__name__)


@bot.schedule_task(minutes=bot.config_manager.get_config_value("kimochi.minutes", []))
def execute():
    logger.info("準備するですよ")
    api = bot.get_account(bot.config_manager.get_config_value("kimochi.account"))
    if api is None:
        logger.warning("アカウントの取得に失敗しました")
    tl = api.home_timeline(count=100)
    random.shuffle(tl)

    for tweet in tl:
        if tweet.favorited:
            continue
        text = tweet.text.replace('\n', ' ')
        logger.debug(f"Text: {text}")
        if '@' in text:
            logger.debug("誰かへのリプライ")
            continue
        text = ' '.join([t for t in text.split(' ') if not (t.startswith('http') or t.startswith('#'))])
        try:
            result = JUMANPP.analysis(text).mrph_list()
        except ValueError:
            logger.debug("analysisの失敗")
            continue
        s = ""
        l = []
        for m in result:
            if m.hinsi == "名詞":
                s += m.midasi
            elif s != "":
                l.append(s)
                s = ""
        if s != "":
            l.append(s)
        logger.debug(f"Noun list: {l}")
        if len(l) == 0:
            logger.debug("名詞がない")
            continue
        random.shuffle(l)
        choice = None
        for t in l:
            if not (max([ord(c) for c in t]) < 128 or len(t) < 2 or '#' in t):
                choice = t
                break
        logger.debug(f"Choice: {choice}")
        if choice is None:
            logger.debug("条件を満たす名詞がない")
            continue
        messages = [
            message["text"]
            for message in bot.config_manager.get_config_value("kimochi.messages", ["{}"])
            if isinstance(message, dict)
            for _ in range(message["ratio"] if "ratio" in message else 1)
        ]
        status = random.choice(messages).format(choice)
        try:
            api.update_status(status=status)
            logger.info(status)
        except tweepy.TweepError as e:
            logger.debug(e)
            continue
        api.create_favorite(tweet.id)
        logger.info("お気に入りでごぜーます！")
        return
    logger.info("ツイートできなかったでごぜーます……")

