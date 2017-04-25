from typing import List

from nbot import bot


@bot.command_task("commands", name="commands_command")
def on_commands_command(_: List[str]):
    print("Command List: {}".format(", ".join(bot.plugin_manager.commands)))


@bot.command_task("execute_task", name="execute_task_command")
def on_execute_task_command(args: List[str]):
    print(args)
    if len(args) > 0:
        task = bot.plugin_manager.get_schedule_task(args[0])
        if task is None:
            print("Taskが見つかりません")
        else:
            task.task()
    else:
        print("引数が足りません")
