from logging import getLogger
from typing import List

from nbot.core import bot

logger = getLogger(__name__)


@bot.command_task("commands")
def on_command_command(_: List[str]):
    logger.info("Command List: {}".format(", ".join(bot.plugin_manager.commands)))
