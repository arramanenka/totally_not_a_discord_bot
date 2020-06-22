import re

import discord
import pycountry

from src.util import find_flags


class TotallyNotBot(discord.Client):
    async def on_ready(self):
        print(f'{self.user} has connected to Discord!')
        for g in self.guilds:
            self.save_guild_member_map(g)

    async def on_message(self, message):
        for mention in message.mentions:
            if mention.id == self.user.id:
                await self.reply_to_direct(message)

    @staticmethod
    async def reply_to_direct(message):
        actual_message = re.sub(r'<.*>', '', message.content).strip()
        if actual_message == 'update map':
            guild = message.channel.guild
            TotallyNotBot.save_guild_member_map(guild)
            await message.channel.send('I am a good boy, I updated your map!',
                                       file=discord.File(filename='map.csv', fp='map.csv'))
        elif actual_message == 'get map':
            await message.channel.send(file=discord.File(filename='map.csv', fp='map.csv'))
        elif actual_message == 'help':
            await message.channel.send(
                'To update map, write \'update map\', to map that was already created, write \'get map\'. I generate '
                'csv for www.datawrapper.de/maps/')
        else:
            await message.channel.send('Command not recognized, try help')

    @staticmethod
    def save_guild_member_map(guild):
        flag_dict = dict()
        for m in guild.members:
            if not m.bot:
                flags = find_flags(m.nick)
                for flag in set(flags):
                    country = pycountry.countries.get(alpha_2=flag)
                    if country is None:
                        if flag == 'EA':
                            country = pycountry.countries.get(alpha_2='ES')
                        elif flag == 'CP':
                            country = pycountry.countries.get(alpha_2='FR')
                        else:
                            print(flag)
                            continue
                    elif country.alpha_3 == 'PRI':
                        country = pycountry.countries.get(alpha_2='US')
                    country_name = country.alpha_3
                    flag_dict[country_name] = flag_dict.get(country_name, 0) + 1
        with open(f'{guild.id}.csv', mode='w+', encoding='utf-8') as csv_file:
            csv_file.write('ISO-Code,count')
            for key, count in flag_dict.items():
                csv_file.write(f'\n{key},{count}')
