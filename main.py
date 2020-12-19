import os
import logging
import discord
from dotenv import load_dotenv

# Modules
from utils import *
from cmd_main import *

# Configure root (global) logger
root_logger = logging.getLogger('')
root_logger.setLevel(logging.NOTSET)
lso = logging.StreamHandler()
lfo = logging.FileHandler('main.log')
lso.setLevel(logging.WARNING)
lfo.setLevel(logging.DEBUG)
format = logging.Formatter('%(asctime)s:%(name)-12s:%(levelname)-8s - %(message)s')
lso.setFormatter(format)
lfo.setFormatter(format)
root_logger.addHandler(lso)
root_logger.addHandler(lfo)
# configure local logger
log = logging.getLogger(__name__)




load_dotenv()
BOT_TOKEN = os.getenv("TOKEN")

class MyClient(discord.Client):
    async def on_ready(self):
        log.info('Logged on as {0}!'.format(self.user))

    async def on_message(self, message):
        log.info('Message from {0.author}: {0.content}'.format(message))

#client = MyClient()
#client.run(BOT_TOKEN)
log.info("running test now")
test()