import discord
from discord.ext import commands
import logging
log = logging.getLogger(__name__)

# put this in utils?
priv_user_ids = ["175786263201185792", "483039138178662400"]
async def is_owner(ctx):
    return ctx.author.id in priv_user_ids

class Cog(commands.Cog, name='General commands'):
    def __init__(self, bot):
        self.bot = bot
        log.info(f"Registered Cog: {self.qualified_name}")

    @commands.command()
    async def i(self, ctx):
        await ctx.send(".")

    @commands.command()
    @commands.check(is_owner)
    async def leave(ctx):
        ctx.guild.leave() # or something like that
