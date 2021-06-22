import db_cache
import logging
log = logging.getLogger(__name__)

prefixes = db_cache.DBCache("cmd_prefix", "guild_id", "prefix")
default_prefix = "./"



async def get(guild_id):
    prefix = await prefixes.get(guild_id)
    if prefix is None:
        await add_or_update(guild_id, default_prefix)
        prefix = await prefixes.get(guild_id)
    return prefix


async def add_or_update(guild_id, new_prefix):
    await prefixes.add_or_update(guild_id, new_prefix)


async def remove(guild_id):
    prefix = await prefixes.get(guild_id)
    if prefix is not None:
        await prefixes.remove(guild_id)
