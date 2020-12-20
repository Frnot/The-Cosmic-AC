import os
import logging
import discord
from dotenv import load_dotenv
#debug
import time

log = logging.getLogger(__name__)

# Enable (all) intents
intents = discord.Intents.all()
client = discord.Client(intents=intents)


@client.event
async def on_ready():
    log.info('Logged on as {0}!'.format(client.user))


@client.event
async def on_message(message):
    log.info('Message from {0.author}: {0.content}'.format(message))


def run_bot():
    load_dotenv()
    BOT_TOKEN = os.getenv("TOKEN")
    client.run(BOT_TOKEN)