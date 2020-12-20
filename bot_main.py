import os
import logging
import discord
from discord.ext import commands
from dotenv import load_dotenv
#debug
import time

log = logging.getLogger(__name__)

# Enable (all) intents
intents = discord.Intents.all()
client = commands.Bot(command_prefix="./", intents=intents)


@client.event
async def on_ready():
    log.info('Logged on as {0}!'.format(client.user))


@client.event
async def on_message(message):
    log.info('Message from {0.author}: {0.content}'.format(message))


@client.command()
async def ping(ctx):
    await ctx.send("pong")
    log.info("Sent pong")


def run_bot():
    load_dotenv()
    BOT_TOKEN = os.getenv("TOKEN")
    client.run(BOT_TOKEN)