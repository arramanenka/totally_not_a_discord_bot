import os
import re
from io import StringIO

import discord
import pandas as pd
import pycountry
from datawrapper import Datawrapper
from discord.utils import get

from src.util import find_flags


class TotallyNotBot(discord.Client):

    def __init__(self, *, loop=None, **options):
        super().__init__(loop=loop, **options)
        self.guild_id = int(os.getenv('GUILD_ID') or '698825558712254494')
        self.open_dm_rule_message_id = int(os.getenv('OPEN_DM_RULE_MESSAGE_ID') or '708210555156037662')
        self.rule_channel_name = os.getenv('RULE_CHANNEL_NAME') or 'rules'
        self.rule_channel = None
        self.dm_rule_guild = None
        self.thank_you_words = ['thanks', 'thx', 'good boi', 'good boy', 'I love you', 'ily', 'love you']
        self.game_object = None
        self.data_wrapper = Datawrapper(access_token=os.getenv('DATAWRAPPER_TOKEN'))

    async def on_ready(self):
        print(f'{self.user} has connected to Discord!')
        guild = discord.utils.find(lambda g: g.id == self.guild_id, self.guilds)
        self.dm_rule_guild = guild
        if guild and self.open_dm_rule_message_id is not None:
            self.rule_channel = discord.utils.find(lambda c: c.name == self.rule_channel_name, guild.channels)
            self.save_guild_member_map(guild)

    async def on_message(self, message):
        if message.content is not None and any(
                p in message.content.lower() for p in ['pizza', 'plzza', 'p1zza', 'pizzã', 'pizz4', 'pizzá']):
            await message.add_reaction('🍍')
        if 'are you pro China' in message.content:
            await message.channel.send('不我不是')
            return
        for mention in message.mentions:
            if mention.id == self.user.id and len(message.mentions) == 1:
                await self.reply_to_direct(message)
                return

    async def reply_to_direct(self, message):
        if message.author.bot:
            return
        actual_message = re.sub(r'<.*>', '', message.content).strip()
        if actual_message.startswith('!'):
            return
        if actual_message == 'map':
            guild = message.channel.guild
            member_map = TotallyNotBot.save_guild_member_map(guild, False)
            await self.send_dm(message.author, member_map)
            await message.channel.send('I am a good boy, I updated your map! Check your dms')
        elif actual_message == 'map iso':
            guild = message.channel.guild
            guild_member_map = TotallyNotBot.save_guild_member_map(guild)
            await self.send_dm(message.author, file=f'{guild.id}.csv')
            self.update_datawrapper_map(guild_member_map)
            await message.channel.send('I am a good boy, I updated your map! Check your dms')
        elif actual_message == 'map png':
            guild_member_map = TotallyNotBot.save_guild_member_map(message.channel.guild)
            self.update_datawrapper_map(guild_member_map)
            await message.channel.send(file=discord.File('AFjgi.png'))
        elif actual_message == 'help':
            await self.send_dm(message.author,
                               message='To get map in dms, write \'map\'. '
                                       'To get map as .csv with iso codes, write \'map iso\''
                                       ' I generate csv for https://www.datawrapper.de/maps/')
        elif any([x in actual_message.lower() for x in self.thank_you_words]):
            peepo_shy = get(message.channel.guild.emojis, name='Peepo_Shy')
            if peepo_shy:
                await message.channel.send(peepo_shy)
            else:
                await message.channel.send('Trying my best ^_^')
        else:
            await message.channel.send('I am so sorry, I did not get what you are saying to me. You can ask me '
                                       'for help any time though')

    @staticmethod
    async def send_dm(member, message=None, file=None):
        await member.create_dm()
        if file is not None:
            await member.dm_channel.send(file=discord.File(filename=file, fp=file))
        else:
            await member.dm_channel.send(message)

    @staticmethod
    def save_guild_member_map(guild, use_iso=True):
        flag_dict = dict()
        for m in guild.members:
            if not m.bot:
                flags = find_flags(m.nick)
                added_flags = []
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
                    if country_name not in added_flags:
                        added_flags.append(country_name)
                        flag_dict.setdefault(country_name, 0)
                        flag_dict[country_name] = flag_dict[country_name] + 1
        results = []
        for key in sorted(flag_dict, key=flag_dict.get):
            result = f'\n{key if use_iso else pycountry.countries.get(alpha_3=key).name},{flag_dict[key]}'
            results.append(result)
        output = ''.join(results)
        with open(f'{guild.id}.csv', mode='w+', encoding='utf-8') as csv_file:
            csv_file.write('ISO-Code,count')
            csv_file.write(output)
        return output

    def update_datawrapper_map(self, guild_member_map):
        self.data_wrapper.add_data('AFjgi', data=pd.read_csv(StringIO(f'ISO-Code,count\n{guild_member_map}')))
        self.data_wrapper.publish_chart('AFjgi')
        self.data_wrapper.export_chart('AFjgi', filepath='AFjgi.png')
