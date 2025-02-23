""" A discord bot used to interact to get times and such """
import logging
import time
import threading
import asyncio
import discord
from discord.ext import commands
from discord import HTTPException
from common.dbms import DBMS


def posh_time(seconds):
    """ Used to convert seconds to days, hours, minutes, and seconds """
    days = int(round(seconds / 86400))
    hours = int(round((seconds % 86400) / 3600))
    minutes = int(round((seconds % 3600) / 60))
    seconds = int(round(seconds % 60))
    return f"{days} days, {hours}h, {minutes}m, {seconds}s"


class DiscordBot(commands.Bot):
    """ DiscordBot class used to create discord bot instance """
    def __init__(self, discord_token, command_prefix: str, dbms : DBMS):
        super().__init__(command_prefix, intents=discord.Intents().all())
        self.dbms = dbms
        self.command_prefix: str = command_prefix
        self.queue = {}
        self.loop = asyncio.get_event_loop()
        self.loop.create_task(self.start(discord_token))
        self.changing_presence = False
        self.time_of_last_lux_request = 0
        self.command_outputs = {
            "help": "this message",
            "top <number>" : "shows the top <number> of runs on a trail"
        }
        self.channels = {
            "fastest_time": 929121402597015685,
            "ban_note": 997942390432206879,
            "new_time": 1166082973385375744
        }
        threading.Thread(target=self.loop.run_forever).start()

    async def send_message_to_channel(self, message, channel_id):
        """ Used to send a message to a channel """
        channel = self.get_channel(channel_id)
        if isinstance(channel, discord.TextChannel):
            await channel.send(message)

    async def on_message(self = None, message = None): # none and none default to allow inheritance
        logging.info("Message sent '%s'", message)
        if message is None:
            return
        if message.author == self.user:
            return
        if message.content.startswith(self.command_prefix + "help"):
            hp = ""
            for command, description in self.command_outputs.items():
                hp += "`!" + command + "` - " + description + "\n"
            await message.channel.send(hp)
        if message.author.id in [id for id in self.queue]:
            leaderboard = await self.dbms.get_leaderboard(
                message.content,
                self.queue[message.author.id]
            )
            leaderboard_str = ""
            for i, player in enumerate(leaderboard):
                name = "**" + player["name"] + "**"
                time1 = float(player["time"])
                num = ""
                if i == 0:
                    num = "🥇 "
                elif i == 1:
                    num = "🥈 "
                elif i == 2:
                    num = "🥉 "
                else:
                    num = i + 1
                verified = player["verified"] == "1"
                if not verified:
                    leaderboard_str += "||"
                leaderboard_str += f"{num} - {time1} - {name}"
                time_id = player['time_id']
                leaderboard_str += "\n"
            try:
                await message.channel.send(
                    f"Top {self.queue[message.author.id]}"
                    f" on {message.content}\n\n{leaderboard_str}"
                )
            except HTTPException:
                await message.channel.send(
                    "Sorry - too many players to display!"
                )
            self.queue.pop(message.author.id)

        if message.content.startswith(self.command_prefix + 'top'):
            try:
                num = int(message.content.split(" ")[1])
            except (IndexError, KeyError):
                num = 3
            self.queue[message.author.id] = num
            await message.channel.send(
                'Please enter the name of the trail you want to check.'
            )
