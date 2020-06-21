import re

import discord


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
            response = 'wow, such empty'
            await message.channel.send(response)
