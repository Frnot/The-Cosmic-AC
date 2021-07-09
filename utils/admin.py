import logging
log = logging.getLogger(__name__)


async def is_server_owner(ctx):
    return ctx.author == ctx.guild.owner

async def can_manage_server(ctx):
    return ctx.author.guild_permissions.manage_guild
