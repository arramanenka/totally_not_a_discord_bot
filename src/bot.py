import asyncio
import os
import re

import discord
import pycountry
from discord.utils import get
from datawrapper import Datawrapper
from io import StringIO
import pandas as pd

from src.discord_game import PickAPersonGame
from src.util import find_flags, check_presence


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
        self.data_wrapper = Datawrapper(access_token = os.getenv('DATAWRAPPER_TOKEN'))

    async def on_ready(self):
        print(f'{self.user} has connected to Discord!')
        guild = discord.utils.find(lambda g: g.id == self.guild_id, self.guilds)
        self.dm_rule_guild = guild
        if guild and self.open_dm_rule_message_id is not None:
            self.rule_channel = discord.utils.find(lambda c: c.name == self.rule_channel_name, guild.channels)
            self.loop.create_task(self.update_rule_roles())
            self.save_guild_member_map(guild)

    async def update_rule_roles(self):
        while True:
            print('checking roles')
            if self.rule_channel is not None and self.open_dm_rule_message_id is not None:
                msg = await self.rule_channel.fetch_message(self.open_dm_rule_message_id)
                rules = dict()
                for r in msg.reactions:
                    users = await r.users().flatten()
                    if r.emoji == '🌕':
                        rules['open'] = users
                    elif r.emoji == '🌗':
                        rules['ask_first'] = users
                    elif r.emoji == '🌑':
                        rules['closed'] = users
                rules.setdefault('open', [])
                rules.setdefault('ask_first', [])
                rules.setdefault('closed', [])
                for member in rules['closed']:
                    if check_presence(member, 'open', rules):
                        rules['open'].remove(member)
                    if check_presence(member, 'ask_first', rules):
                        rules['ask_first'].remove(member)
                for member in rules['ask_first']:
                    if check_presence(member, 'open', rules):
                        rules['open'].remove(member)
                closed_dms_role_name = 'Closed DMs'
                ask_first_dms_role_name = 'Ask First DMs'
                open_dms_role_name = 'Open DMs'
                all_roles = {open_dms_role_name, ask_first_dms_role_name, closed_dms_role_name}
                await self.assign_role_if_not_present(rules['open'], open_dms_role_name, all_roles)
                await self.assign_role_if_not_present(rules['ask_first'], ask_first_dms_role_name, all_roles)
                await self.assign_role_if_not_present(rules['closed'], closed_dms_role_name, all_roles)
            await asyncio.sleep(3600)
        pass

    async def assign_role_if_not_present(self, members, role_name, conflicting_roles=None):
        for member in members:
            if type(member) is discord.User:
                # it is a member, who left server, so we cannot assign or remove any roles
                continue
            if conflicting_roles is not None:
                for conflicting_role in conflicting_roles:
                    if conflicting_role == role_name:
                        continue
                    found_role = discord.utils.find(lambda role: role.name == conflicting_role, member.roles)
                    if found_role is not None:
                        await self.remove_role_from_member(member, conflicting_role)
            found_role = discord.utils.find(lambda role: role.name == role_name, member.roles)
            if found_role is None:
                await self.assign_role_to_member(member, role_name)
                pass
        pass

    async def manage_roles_for_user(self, member, role, action):
        actual_role = discord.utils.get(self.dm_rule_guild.roles, name=role)
        if actual_role is not None:
            await action(actual_role)
        else:
            print(f'Could not find role {role} on server, so cannot assign it to {member}')
        pass

    async def assign_role_to_member(self, member, role):
        async def assign_role(actual_role):
            await member.add_roles(actual_role)
            print(f'assigned {role} to  {member}')

        await self.manage_roles_for_user(member, role, assign_role)

    async def remove_role_from_member(self, member, role):
        async def remove_role(actual_role):
            await member.remove_roles(actual_role)
            print(f'removed role {role} from {member}')

        await self.manage_roles_for_user(member, role, remove_role)

    async def on_message(self, message):
        if message.content is not None and any(
                p in message.content.lower() for p in ['pizza', 'plzza', 'p1zza', 'pizzã', 'pizz4', 'pizzá']):
            await message.add_reaction('🍍')
        if 'are you pro China' in message.content:
            await message.channel.send('不我不是')
            return
        # if message.guild is None and message.author.id != self.user.id:
        #     await PickAPersonGame.process_direct(message, self.game_object)
        for mention in message.mentions:
            if mention.id == self.user.id:
                await self.reply_to_direct(message)
                return

    async def reply_to_direct(self, message):
        if message.author.bot:
            return
        actual_message = re.sub(r'<.*>', '', message.content).strip()
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
            await message.channel.send(file='AFjgi.png')
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
        # elif actual_message.startswith('game_'):
        #     await self.process_game_request(message, actual_message)
        else:
            await message.channel.send('Command not recognized, try help')

    async def process_game_request(self, message, actual_message):
        if get(message.author.roles, name='Maintenance Key') is None \
                and get(message.author.roles, name='Moderator') is None:
            await message.channel.send(f'Sorry, {message.author.nick}, you ain\'t a mod, or a beautiful maintainer')
            return
        if actual_message.startswith('game_start'):
            if self.game_object is None:
                if actual_message == 'game_start pick-a-person':
                    self.game_object = PickAPersonGame()
                    await self.game_object.start(message)
                else:
                    await message.channel.send("Unrecognized game. Please try again")
            else:
                await message.channel.send("Another game is running, please try later")
        elif actual_message.startswith('game_stop'):
            if self.game_object is not None:
                self.game_object = None
        elif self.game_object is None:
            await message.channel.send("No game in progress, check back later")
        elif actual_message.startswith('game_reset'):
            self.game_object.delete_all_confessions()
        else:
            await self.game_object.process_game_request(message, actual_message)

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
        self.data_wrapper.export_chart('AFjgi', width=1920, filepath='AFjgi.png')
