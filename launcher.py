import os

from src.bot import TotallyNotBot
from src.keep_alive import keep_alive

keep_alive()

TOKEN = os.getenv('DISCORD_TOKEN')

client = TotallyNotBot()

client.run(TOKEN)
