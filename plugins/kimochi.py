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
        logger.debug("Text: {}".format(text))
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
        logger.debug("Noun list: {}".format(l))
        if len(l) == 0:
            logger.debug("名詞がない")
            continue
        random.shuffle(l)
        choice = None
        for t in l:
            if not (max([ord(c) for c in t]) < 128 or len(t) < 2 or '#' in t):
                choice = t
                break
        logger.debug("Choice: {}".format(choice))
        if choice is None:
            logger.debug("条件を満たす名詞がない")
            continue
        try:
            if random.randint(0, 3) == 3:
                status = "{}の気持ちがつかめなかったでごぜーます……".format(choice)
            else:
                status = "{}の気持ちになるですよ".format(choice)
            api.update_status(status=status)
            logger.info(status)
        except tweepy.TweepError as e:
            logger.debug(e)
            continue
        api.create_favorite(tweet.id)
        logger.info("お気に入りでごぜーます！")
        return
    logger.info("ツイートできなかったでごぜーます……")

