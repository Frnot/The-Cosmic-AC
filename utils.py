from datetime import datetime
import logging
log = logging.getLogger(__name__)

#class Utils:
priv_user_ids = [175786263201185792]
async def is_owner(ctx):
    return ctx.author.id in priv_user_ids
