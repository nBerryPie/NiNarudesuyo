# coding: utf-8
from io import TextIOWrapper
from sys import stdin, stdout, stderr
from nbot import NBot

if __name__ == "__main__":
    stdin = TextIOWrapper(stdin.buffer, encoding='utf-8')
    stdout = TextIOWrapper(stdout.buffer, encoding='utf-8')
    stderr = TextIOWrapper(stderr.buffer, encoding='utf-8')
    bot = NBot()
    bot.run()

