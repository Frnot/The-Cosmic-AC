import discord
from discord.ext import commands
import logging
import random
import utils.admin
import utils.general
log = logging.getLogger(__name__)


class Cog(commands.Cog, name='General commands'):
    def __init__(self, bot):
        self.bot = bot
        log.info(f"Registered Cog: {self.qualified_name}")


    # debug ping
    @commands.command()
    async def ping(self, ctx):
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
    @commands.check(utils.admin.is_server_owner)
    async def purge(self, ctx, ammount=100):
        num = int(ammount)
        log.info(f"deleting {ammount} messages in channel: {ctx.channel} in guild: {ctx.guild}")
        await ctx.channel.purge(limit=num)

    # flip a coin
    @commands.command()
    async def flip(self, ctx):
        flip = random.randint(0, 1)
        if flip == 1:
            result = "HEADS"
        else:
            result = "TAILS"

        embed = discord.Embed(
            color=discord.Colour(utils.rng.random_color()),
            title=f"Flipping a Coin",
            description=f"You flipped: {result}")
        await ctx.send(embed = embed)
    
    @commands.command()
    async def random(self, ctx, start, end):
        num = random.randint(int(start), int(end))

        embed = discord.Embed(
            color=discord.Colour(utils.rng.random_color()),
            title=f"Random number  {start} - {end}",
            description=f"Value: {num}")
        await ctx.send(embed = embed)

    @random.error
    async def random_error(self, ctx, exception):
        # if not enough args
        # if isinstance(exception, commands.NotOwner):
            #await ctx.send("You do not have permission to use this command")
        #else:
        await ctx.send(f"error: {exception}")
