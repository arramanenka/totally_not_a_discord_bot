import os

from src.bot import TotallyNotBot

TOKEN = os.getenv('DISCORD_TOKEN')

client = TotallyNotBot()

client.run(TOKEN)
