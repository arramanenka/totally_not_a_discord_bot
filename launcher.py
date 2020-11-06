import os

import discord

from src.bot import TotallyNotBot

TOKEN = os.getenv('DISCORD_TOKEN')
intents = discord.Intents.default()
intents.members = True

client = TotallyNotBot(intents=intents)

client.run(TOKEN)
