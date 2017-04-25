from typing import List

from nbot import bot


@bot.command_task("commands", name="commands_command")
def on_commands_command(_: List[str]):
    print("Command List: {}".format(", ".join(bot.plugin_manager.commands)))
