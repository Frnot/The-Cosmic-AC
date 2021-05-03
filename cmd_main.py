import discord
from discord.ext import commands
import db
import logging
import time
import utils
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
    
    # bulk delete the last few messages
    @commands.command()
    async def purge(self, ctx, ammount=100):
        num = int(ammount)
        log.info(f"deleting {ammount} messages in channel: {ctx.channel} in guild: {ctx.guild}")
        await ctx.channel.purge(limit=num)

    # leave server
    @commands.command()
    @commands.check(utils.is_owner)
    async def leave(self, ctx):
        log.info("leave command fired")
        await ctx.guild.leave() # or something like that


    # set status
    @commands.command()
    @commands.check(utils.is_owner)
    async def status(self, ctx, action: utils.to_lower, status):
        if action == "playing":
            actiontype = discord.ActivityType.playing
        elif action == "streaming":
            actiontype = discord.ActivityType.streaming
        elif action in ("listening", "listening to"):
            actiontype = discord.ActivityType.listening
        elif action == "watching":
            actiontype = discord.ActivityType.watching
        elif action in ("competing", "competing in"):
            actiontype = discord.ActivityType.competing
        
        await self.bot.change_presence(activity=discord.Activity(name=status, type=actiontype))

        log.info(f"setting status to {actiontype.name} `{status}`")
        await self.send_confirmation(ctx)

    @status.error
    async def status_error(self, ctx, exception):
        await ctx.send("test")
        await ctx.send(f"error: {exception}")
        

    @commands.command()
    @commands.check(utils.is_owner)
    async def votekick(self, ctx, *, member: discord.Member):
        pass

    # Module Functions
    async def send_confirmation(self, ctx):
        # Confirm command (and delete command 30 seconds later)
        await ctx.message.add_reaction("✅")
        await ctx.message.delete(delay=30)
