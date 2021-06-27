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
        self.celebration_words = ['congratulations', 'congrats']
        self.weed_words = ['420', 'pot']
        self.map_generator = MapGenerator()

    async def on_ready(self):
        print(f'{self.user} has connected to Discord!')

    async def on_message(self, message):
        if message.content is not None:
            lowered = message.content.lower()
            if any(p in lowered for p in self.pineapple_worthy_words):
                await message.add_reaction('🍍')
            if any(p in lowered for p in self.weed_words):
                await message.add_reaction('🥦')
            if re.match(r'.*\b(eh|sorry)\b.*', lowered):
                await message.add_reaction('🇨🇦')
            if any(p in lowered for p in self.celebration_words):
                await message.add_reaction('🎉')
                await message.add_reaction('✨')

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
            await self.create_map(message)
        elif actual_message == 'map png':
            await self.create_map(message, True)
        elif actual_message == 'help':
            await self.send_dm(message.author,
                               message='To get map as .csv with iso codes, write \'map iso\' '
                                       'To get map as image, write \'map png\' '
                                       'I generate maps based on country flags I detect in people\'s nicknames')
            await message.channel.send('Instructions are top secret, but I have sent them in your dms.',
                                       reference=message, mention_author=False)
        elif any([x in actual_message.lower() for x in self.thank_you_words]):
            peepo_shy = get(message.channel.guild.emojis, name='Peepo_Shy')
            if peepo_shy:
                await message.add_reaction(peepo_shy)
            else:
                await message.add_reaction('😳')

    async def create_map(self, message, image=False):
        await message.channel.send('Please wait a second, I will look up all members and generate the map asap')
        guild_member_map = await MapGenerator.save_guild_member_map(message.channel.guild)
        if image:
            image_name = f'{message.channel.guild.id}.png'
            self.map_generator.save_map_as_png(guild_member_map, image_name, message.channel.guild.name)
            await message.channel.send(file=discord.File(image_name), reference=message)
        else:
            await self.send_dm(message.author, message='here is your map ❤️', file=f'{message.channel.guild.id}.csv')

    @staticmethod
    async def send_dm(member, message=None, file=None):
        await member.create_dm()
        if file is not None:
            await member.dm_channel.send(file=discord.File(filename=file, fp=file))
        else:
            await member.dm_channel.send(message)
