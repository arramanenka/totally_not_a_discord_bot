import re

import discord
from discord.utils import get

from src.map import MapGenerator


class TotallyNotBot(discord.Client):

    def __init__(self, *, loop=None, **options):
        super().__init__(loop=loop, **options)
        self.thank_you_words = ['thanks', 'thank', 'thx', 'good', 'ily', 'love', 'adore', 'like']
        self.pineapple_worthy_words = ['pizza', 'plzza', 'p1zza', 'pizzã', 'pizz4', 'pizzá', 'pineapple', 'ananas',
                                       'ананас', '🍍']
        self.game_object = None
        self.map_generator = MapGenerator()

    async def on_ready(self):
        print(f'{self.user} has connected to Discord!')

    async def on_message(self, message):
        if message.content is not None and any(
                p in message.content.lower() for p in self.pineapple_worthy_words):
            await message.add_reaction('🍍')
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
        elif actual_message == 'map iso':
            await message.channel.send('Please wait a second, I will look up all members and generate the map asap')
            guild = message.channel.guild
            await MapGenerator.save_guild_member_map(guild)
            await self.send_dm(message.author, message='here is your map :heart:', file=f'{guild.id}.csv')
        elif actual_message == 'map png':
            await message.channel.send('Please wait a second, I will look up all members and generate the map asap')
            guild_member_map = await MapGenerator.save_guild_member_map(message.channel.guild)
            self.map_generator.update_datawrapper_map(guild_member_map)
            await message.channel.send(file=discord.File('ovAEX.png'), reference=message)
        elif actual_message == 'help':
            await self.send_dm(message.author,
                               message='To get map as .csv with iso codes, write \'map iso\' '
                                       'To get map as image, write \'map png\' '
                                       'I generate csv for https://www.datawrapper.de/maps/')
            await message.channel.send('Instructions are top secret, but I have sent them in your dms.',
                                       reference=message, mention_author=False)
        elif any([x in actual_message.lower() for x in self.thank_you_words]):
            peepo_shy = get(message.channel.guild.emojis, name='Peepo_Shy')
            if peepo_shy:
                await message.add_reaction(peepo_shy)
            else:
                await message.add_reaction('😳')

    @staticmethod
    async def send_dm(member, message=None, file=None):
        await member.create_dm()
        if file is not None:
            await member.dm_channel.send(file=discord.File(filename=file, fp=file))
        else:
            await member.dm_channel.send(message)
