import os
import logging
import discord
from dotenv import load_dotenv

log = logging.getLogger(__name__)


class MyClient(discord.Client):
    async def on_ready(self):
        log.info('Logged on as {0}!'.format(self.user))

    async def on_message(self, message):
        log.info('Message from {0.author}: {0.content}'.format(message))

    #async def on_message(self, message):
        


def run_bot():
    load_dotenv()
    BOT_TOKEN = os.getenv("TOKEN")
    client = MyClient()
    client.run(BOT_TOKEN)