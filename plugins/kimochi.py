# coding: utf-8
from pyknp import Jumanpp
import random
import tweepy

from nbot import NBot

EXECUTE_MINUTES = [i for i in range(60) if i % 15 == 0]
JUMANPP = Jumanpp()


def execute(bot: NBot):
    logger = bot.logger
    logger.info("準備するですよ")
    api = bot.get_account("ninarudesuyo")
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
        result = [
            m
            for t in text.split(' ') if not t.startswith("http")
            for m in JUMANPP.analysis(t).mrph_list()
        ]
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
                api.update_status(status="{}の気持ちがつかめなかったでごぜーます……".format(choice))
            else:
                api.update_status(status="{}の気持ちになるですよ".format(choice))
        except tweepy.TweepError as e:
            logger.debug(e)
            continue
        api.create_favorite(tweet.id)
        logger.info("{}でごぜーますよ！".format(choice))
        return
    logger.info("ツイートできなかったでごぜーます……")

