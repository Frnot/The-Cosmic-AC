import db_cache
import logging
log = logging.getLogger(__name__)

blacklists = db_cache.DBCache("blacklist", "guild_id", "blacklist_set", True)



async def add_word(guild_id, word):
    word = scrub(word)
    word_set = await blacklists.get(guild_id)
    if word_set is None:
        word_set = set()

    log.debug(f"Adding word '{word}' to blacklist for guild id: {guild_id}")
    word_set.add(word)
    await blacklists.add_or_update(guild_id, word_set)



async def remove_word(guild_id, word):
    word = scrub(word)
    word_set = await blacklists.get(guild_id)
    if word_set is None:
            log.debug(f"Cannot remove {word} from blacklist for guild id: {guild_id}")
    else:
        if word in word_set:
            log.debug(f"Removed word '{word}' from blacklist for guild id: {guild_id}")
            word_set.remove(word)
            await blacklists.add_or_update(guild_id, word_set)
            return True
        else:
            log.debug(f"Word '{word}' does not exist in the blacklist for guild id: {guild_id}")
            return False



async def get(guild_id):
    return await blacklists.get(guild_id)



async def clear_blacklist(guild_id):
    word_set = await blacklists.get(guild_id)
    if word_set is None:
        return False
    else:
        word_set.clear()
        await blacklists.add_or_update(guild_id, word_set)
        return True



async def sync_blacklists(bot):
    member_guild_ids = set([guild.id for guild in bot.guilds])
    cached_guild_ids = await blacklists.get_keys()

    log.debug("Pruning orphaned blacklists")
    for cached_guild_id in cached_guild_ids:
        if cached_guild_id not in member_guild_ids:
            await blacklists.remove(cached_guild_id)

    log.debug("Loading blacklists for member guilds into cache")
    for member_guild_id in member_guild_ids:
        if await blacklists.get(member_guild_id) is None:
            await blacklists.add_or_update(member_guild_id, set())



def scrub(word):
    return word.lower()
