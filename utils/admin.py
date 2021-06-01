import logging
log = logging.getLogger(__name__)


async def is_owner(ctx):
    return await ctx.bot.is_owner(ctx.author) 


async def is_server_owner(ctx):
    return ctx.author == ctx.guild.owner
