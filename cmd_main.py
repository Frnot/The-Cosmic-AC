import discord
from discord.ext import commands
import utils
import logging
log = logging.getLogger(__name__)

class Cog(commands.Cog, name='General commands'):
    def __init__(self, bot):
        self.bot = bot
        log.info(f"Registered Cog: {self.qualified_name}")

    @commands.command()
    async def i(self, ctx):
        await ctx.send(".")

    @commands.command()
    @commands.check(utils.is_owner)
    async def leave(self, ctx):
        log.info("leave command fired")
        await ctx.guild.leave() # or something like that

