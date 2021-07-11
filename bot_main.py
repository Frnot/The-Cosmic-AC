import sys
import logging
import discord
from discord.ext import commands as dcommands
from dotenv import load_dotenv
if sys.version_info >= (3, 8):
    from importlib import metadata
else:
    import importlib_metadata as metadata

# Import modules
import db
import commands.admin, commands.general
from modules import blacklist, prefix, server_management, snitch, voting


log = logging.getLogger(__name__)

version = metadata.version('CosmicAC')




def run_bot(bot_token):
    log.info(f"Running version v{version}")

    # Load Database
    log.info("Loading database")
    db.load()

    # Create bot
    global bot
    bot = Bot(command_prefix=guild_prefix, intents=discord.Intents.all(), \
                        activity=discord.Activity(name=f"v{version}", type=discord.ActivityType.playing))

    # Load modules
    bot.add_cog(commands.admin.Cog(bot))
    bot.add_cog(commands.general.Cog(bot))

    bot.add_cog(blacklist.Cog(bot))
    bot.add_cog(prefix.Cog(bot))
    bot.add_cog(server_management.Cog(bot))
    bot.add_cog(snitch.Cog(bot))
    bot.add_cog(voting.Cog(bot))

    # Run bot
    bot.run(bot_token)

    # Cleanup
    db.close()



async def guild_prefix(bot, message):
    bot
    prefix_return = await bot.get_cog('Prefix').get(message.guild.id)
    return dcommands.when_mentioned_or(prefix_return)(bot, message)


class Bot(dcommands.Bot):
    async def on_ready(self):
        log.info(f"Logged on as {bot.user}!\nReady.")
