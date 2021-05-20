import logging
log = logging.getLogger(__name__)


owner_ids = [175786263201185792]
async def is_owner(ctx):
    return ctx.author.id in owner_ids

async def is_server_owner(ctx):
    return ctx.author == ctx.guild.owner
