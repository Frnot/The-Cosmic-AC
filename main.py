import os
import logging
import discord


# Modules
from utils import *
from cmd_main import *
import bot_main

# Configure root (global) logger
root_logger = logging.getLogger('')
root_logger.setLevel(logging.NOTSET)
lso = logging.StreamHandler()
lfo = logging.FileHandler('main.log', encoding="UTF-8")
lso.setLevel(logging.WARNING)
lfo.setLevel(logging.DEBUG)
format = logging.Formatter('%(asctime)s:%(name)-12s:%(levelname)-8s - %(message)s')
lso.setFormatter(format)
lfo.setFormatter(format)
root_logger.addHandler(lso)
root_logger.addHandler(lfo)
# configure local logger
log = logging.getLogger(__name__)



log.info("running test now")
test()

log.info("Starting bot")
bot_main.run_bot()