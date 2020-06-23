import asyncio
import os
import re

import discord
import pycountry

from src.util import find_flags, check_presence


class TotallyNotBot(discord.Client):

    def __init__(self, *, loop=None, **options):
        super().__init__(loop=loop, **options)
        self.guild_id = int(os.getenv('GUILD_ID') or '698825558712254494')
        self.open_dm_rule_message_id = int(os.getenv('OPEN_DM_RULE_MESSAGE_ID') or '708210555156037662')
        self.rule_channel_name = os.getenv('RULE_CHANNEL_NAME') or 'rules'
        self.rule_channel = None
        self.dm_rule_guild = None

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
                ask_first_dms_role_name = 'Ask First'
                open_dms_role_name = 'Open DMs'
                all_roles = {open_dms_role_name, ask_first_dms_role_name, closed_dms_role_name}
                await self.assign_role_if_not_present(rules['open'], open_dms_role_name, all_roles)
                await self.assign_role_if_not_present(rules['ask_first'], ask_first_dms_role_name, all_roles)
                await self.assign_role_if_not_present(rules['closed'], closed_dms_role_name, all_roles)
            await asyncio.sleep(3)
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
            print(f'Could not find role {role} on server')
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
        for mention in message.mentions:
            if mention.id == self.user.id:
                await self.reply_to_direct(message)

    async def reply_to_direct(self, message):
        if message.author.bot:
            return
        actual_message = re.sub(r'<.*>', '', message.content).strip()
        if actual_message == 'update map':
            guild = message.channel.guild
            TotallyNotBot.save_guild_member_map(guild)
            await self.send_dm(message.author, file=f'{guild.id}.csv')
            await message.channel.send('I am a good boy, I updated your map! Check your dms')
        elif actual_message == 'get map':
            await self.send_dm(message.author, file=f'{message.channel.guild.id}.csv')
            await message.channel.send('Sent csv to your dms')
        elif actual_message == 'help':
            await self.send_dm(message.author,
                               message='To update map, write \'update map\', to map that was already created, '
                                       'write \'get map\'. I generate csv for https://www.datawrapper.de/maps/')
        else:
            await message.channel.send('Command not recognized, try help')

    @staticmethod
    async def send_dm(member, message=None, file=None):
        await member.create_dm()
        if file is not None:
            await member.dm_channel.send(file=discord.File(filename=file, fp=file))
        else:
            await member.dm_channel.send(message)

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
