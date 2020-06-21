import discord


class TotallyNotBot(discord.Client):
    async def on_ready(self):
        print(f'{self.user} has connected to Discord!')
