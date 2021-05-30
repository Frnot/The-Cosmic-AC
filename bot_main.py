import os
import sys
import logging
import discord
from discord.ext import commands
from dotenv import load_dotenv
if sys.version_info >= (3, 8):
    from importlib import metadata
else:
    import importlib_metadata as metadata

# Import modules
import db
import cmd_main
import snitch
import blacklist
import server_management
import voting

log = logging.getLogger(__name__)

# Enable (all) intents
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="./", intents=intents)


@bot.event
async def on_ready():
    log.info(f"Logged on as {bot.user}!")
    
    version = metadata.version('CosmicAC')
    log.info(f"setting status to playing `v{version}`")
    await bot.change_presence(activity=discord.Activity(name=f"v{version}", type=discord.ActivityType.playing))



def run_bot():
    # Get token from .env file
    load_dotenv()
    BOT_TOKEN = os.getenv("TOKEN")   

    # Load modules
    bot.add_cog(cmd_main.Cog(bot))
    bot.add_cog(snitch.Cog(bot))
    bot.add_cog(blacklist.Cog(bot))
    bot.add_cog(server_management.Cog(bot))
    bot.add_cog(voting.Cog(bot))

    # Load Database
    log.info("Loading database")
    db.load()

    # Start the bot
    bot.run(BOT_TOKEN)

    # after the bot is somehow stopped
    # run cleanup
    db.exit()
