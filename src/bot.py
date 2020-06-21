import re

import discord
import json

from src.util import find_flags


class TotallyNotBot(discord.Client):
    async def on_ready(self):
        print(f'{self.user} has connected to Discord!')

    async def on_message(self, message):
        for mention in message.mentions:
            if mention.id == self.user.id:
                await self.reply_to_direct(message)

    @staticmethod
    async def reply_to_direct(message):
        actual_message = re.sub(r'<.*>', '', message.content).strip()
        if actual_message == 'map':
            flag_dict = dict()
            for m in message.channel.guild.members:
                if not m.bot:
                    flags = find_flags(message.author.nick)
                    for flag in flags:
                        flag_dict[flag] = flag_dict.get(flag, 0) + 1
            await message.channel.send(json.dumps(flag_dict))
