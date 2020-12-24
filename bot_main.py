import os
import logging
import discord
from discord.ext import commands
from dotenv import load_dotenv
# Import modules
import db
import cmd_main
import snitch

log = logging.getLogger(__name__)

# Enable (all) intents
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="./", intents=intents)


@bot.event
async def on_ready():
    log.info('Logged on as {0}!'.format(bot.user))


def run_bot():
    # Get token from .env file
    load_dotenv()
    BOT_TOKEN = os.getenv("TOKEN")   
    
    # Load modules
    bot.add_cog(cmd_main.Cog(bot))
    bot.add_cog(snitch.Cog(bot))
    
    # Start the bot
    bot.run(BOT_TOKEN)

    # after the bot is somehow stopped
    # run cleanup
    db.exit()
