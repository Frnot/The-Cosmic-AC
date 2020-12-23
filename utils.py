from datetime import datetime
import logging

#class Utils:
priv_user_ids = [175786263201185792, 483039138178662400]
async def is_owner(ctx):
    return ctx.author.id in priv_user_ids