import discord
from discord.ext import commands
import logging
log = logging.getLogger(__name__)

def test():
    log.warning('testing')


priv_user_ids = ["175786263201185792", "483039138178662400"]
async def is_owner(ctx):
    return ctx.author.id in priv_user_ids

class Cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        log.info("Cog class has been constructed")

    @commands.command()
    async def i(self, ctx):
        await ctx.send(".")
        log.info("Sent pong")

    @commands.command()
    @commands.check(is_owner)
    async def leave(ctx):
        ctx.guild.leave() # or something like that