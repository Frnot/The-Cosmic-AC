import discord
from discord.ext import commands
import utils
import logging
log = logging.getLogger(__name__)


class Cog(commands.Cog, name='General commands'):
    def __init__(self, bot):
        self.bot = bot
        log.info(f"Registered Cog: {self.qualified_name}")

    # debug ping
    @commands.command()
    async def i(self, ctx):
        await ctx.send(".")

    @commands.command()
    async def listroles(self, ctx):
        role_list = ctx.guild.roles
        for role in role_list:
            await ctx.send(f"Name: `{role.name}` - ID: `{role.id}`")

    # wipe a chat the old fashioned way
    @commands.command()
    async def nukechat(self, ctx):
        log.info(f"nuking channel: {ctx.channel} in guild: {ctx.guild}")
        await ctx.channel.purge()

    # leave server
    @commands.command()
    @commands.check(utils.is_owner)
    async def leave(self, ctx):
        log.info("leave command fired")
        await ctx.guild.leave() # or something like that

    @commands.command()
    @commands.check(utils.is_owner)
    async def setstatus(self, ctx, *, status):
        log.info(f"setting status to `{status}`")
        game = discord.Game(status)
        await self.bot.change_presence(activity=game)
        # Confirm command (and delte it 5 seconds later)
        message = await ctx.send("Okay")
        await message.delete(5)
