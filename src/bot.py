import re

import discord
import pycountry

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
        if actual_message == 'update map':
            flag_dict = dict()
            for m in message.channel.guild.members:
                if not m.bot:
                    flags = find_flags(message.author.nick)
                    for flag in set(flags):
                        country_name = pycountry.countries.get(alpha_2=flag).name
                        flag_dict[country_name] = flag_dict.get(country_name, 0) + 1
            with open('map.csv', mode='w+', encoding='utf-8') as csv_file:
                csv_file.write('Name,count')
                for key, count in flag_dict.items():
                    csv_file.write(f'\n{key},{count}')
            await message.channel.send('updated')
