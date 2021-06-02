import os
import sys
from discord.ext import commands
import logging
import utils.admin
import utils.general
log = logging.getLogger(__name__)

restart = False

class Cog(commands.Cog, name='General commands'):
    def __init__(self, bot):
        self.bot = bot
        log.info(f"Registered Cog: {self.qualified_name}")


    # leave server
    @commands.command()
    @commands.check(utils.admin.is_owner)
    async def leave(self, ctx):
        log.info(f"Recieved leave command in guild {ctx.guild.name}")
        await ctx.guild.leave()

    @commands.command()
    @commands.check(utils.admin.is_owner)
    async def die(self, ctx):
        log.info("Received shutdown command")
        await ctx.bot.close()

    @commands.command()
    @commands.check(utils.admin.is_owner)
    async def update(self, ctx):
        global restart
        restart = True

        async with ctx.channel.typing():
            await ctx.send("Updating...")
            log.info("Running Updates")

            os.system("git stash")
            os.system("git pull")
            os.system(f"\"{sys.executable}\" -m pip install .")
            log.info("Updates done. Restarting main process")

        await ctx.bot.close()
