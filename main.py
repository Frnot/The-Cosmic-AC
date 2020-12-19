import os
import logging
import discord
from dotenv import load_dotenv

# Modules
from utils import *

log = logging.getLogger(__name__)
load_dotenv()
BOT_TOKEN = os.getenv("TOKEN")

class MyClient(discord.Client):
    async def on_ready(self):
        log('Logged on as {0}!'.format(self.user), 3)

    async def on_message(self, message):
        log('Message from {0.author}: {0.content}'.format(message), 3)

client = MyClient()
client.run(BOT_TOKEN)
