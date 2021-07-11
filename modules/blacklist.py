import discord
from discord.ext import commands
import db_cache
from fuzzysearch import find_near_matches
import time
import utils
import logging
log = logging.getLogger(__name__)



class Cog(commands.Cog, name='Blacklist'):
    def __init__(self, bot):
        self.bot = bot
        self.blacklists = db_cache.DBCache("blacklist", "guild_id", "blacklist_set", True)
        log.info(f"Registered Cog: {self.qualified_name}")




    ##### Commands #####

    @commands.group(name="blacklist")
    @commands.check(utils.admin.is_server_owner)
    async def blacklist(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send('Invalid blacklist command')

    @blacklist.command()
    async def add(self, ctx, *args):
        added, existing = await self.add_words(ctx.guild.id, args)
        if added:
            await ctx.send(f"Added `{'`, `'.join(added)}` to blacklist")
        if existing:
            await ctx.send(f"`{'`, `'.join(existing)}` already in blacklist")

    @blacklist.command()
    async def remove(self, ctx, *args):
        removed, not_exist = await self.remove_words(ctx.guild.id, args)
        if removed:
            await ctx.send(f"Removed `{'`, `'.join(removed)}` from blacklist")
        if not_exist:
            await ctx.send(f"Blacklist does not contain `{'`, `'.join(not_exist)}`")

    @blacklist.command()
    async def clear(self, ctx):
        stat = await self.clear_blacklist(ctx.guild.id)
        if stat is None:
            await ctx.send(f"There are no blacklisted words in this server")
        else:
            await ctx.send(f"Cleared blacklisted words for `{ctx.guild.name}`")

    @blacklist.command()
    async def show(self, ctx):
        wordlist = await self.get(ctx.guild.id)
        if not wordlist:
            message = "There are no blacklisted words in this server"
        else:
            message = f"Blacklisted words: `{'`, `'.join(wordlist)}`"
        await ctx.send(message)

    @blacklist.error
    async def blacklist_error(self, ctx, exception):
        await ctx.send(f"error: {exception}")




    ##### Events #####

    @commands.Cog.listener()
    async def on_ready(self):
        log.info("Loading blacklist database into cache")
        time_start = time.perf_counter()
        await self.sync_blacklists(self.bot)
        time_end = time.perf_counter()
        log.info(f"Loading blacklist database into cache: complete in {time_end - time_start:0.6f} seconds")

    # Optimize when necessary (guild count is sufficiently large)
    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        log.info("Creating empty blacklist for new guild")
        time_start = time.perf_counter()
        await self.sync_blacklists(self.bot)
        time_end = time.perf_counter()
        log.info(f"Creating empty blacklist for new guild: complete in {time_end - time_start:0.6f} seconds")

    # Optimize when necessary (guild count is sufficiently large)
    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        log.info("Removing blacklist for expired guild")
        time_start = time.perf_counter()
        await self.sync_blacklists(self.bot)
        time_end = time.perf_counter()
        log.info(f"Removing blacklist for expired guild: complete in {time_end - time_start:0.6f} seconds")

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.author.bot:
            # perform a shallow copy on word_set to avoid race condition
            word_set = set(await self.get(message.guild.id))

            test_message = message.content.lower()

            for word in word_set:
                l_dist = 1
                word_length = len(word)
                if word_length <= l_dist + 1:
                    l_dist = word_length - 1
                    if l_dist < 0: l_dist = 0
                
                match = find_near_matches(word, test_message, max_l_dist=l_dist)

                if match:
                    word = match[0].matched
                    distance = match[0].dist
                    log.info(f"Removing message \"{message.content}\" from {message.author.display_name} in #{message.channel.name}@{message.guild.name} - matched blacklisted word: \"{word}\" with distance of {distance}")
                    try:
                        await message.delete()
                        log.debug(f"Removed message")
                    except discord.NotFound:
                        log.debug(f"Message does not exist. It has already been removed")
                    break

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        await self.on_message(after)




    ##### Model #####

    async def add_words(self, guild_id, words):
        added = []
        error = []
        word_set = await self.blacklists.get(guild_id)
        if word_set is None: 
            log.debug(f"No blacklist found for guild id: {guild_id}")
            word_set = set()

        for word in words:
            word = self.scrub(word)
            if word in word_set:
                error.append(word)
            else:
                log.debug(f"Adding word '{word}' to blacklist for guild id: {guild_id}")
                word_set.add(word)
                added.append(word)

        if added:
            await self.blacklists.add_or_update(guild_id, word_set)
        return (added, error)


    async def remove_words(self, guild_id, words):
        removed = []
        error = []
        word_set = await self.blacklists.get(guild_id)
        
        if word_set is None:
            log.debug(f"Cannot remove word from blacklist for guild id: '{guild_id}'. Blacklist is empty")
        else:
            for word in words:
                word = self.scrub(word)
                if word in word_set:
                    log.debug(f"Removed word '{word}' from blacklist for guild id: {guild_id}")
                    word_set.remove(word)
                    removed.append(word)
                else:
                    log.debug(f"Word '{word}' does not exist in the blacklist for guild id: {guild_id}")
                    error.append(word)

        if removed:
            await self.blacklists.add_or_update(guild_id, word_set)
        return (removed, error)


    async def get(self, guild_id):
        return await self.blacklists.get(guild_id)


    async def clear_blacklist(self, guild_id):
        word_set = await self.blacklists.get(guild_id)
        if word_set is None:
            log.debug(f"Cannot clear blacklist for guild id: {guild_id}. Blacklist is empty")
            return False
        else:
            log.debug(f"Clearing blacklist for guild id: {guild_id}")
            word_set.clear()
            await self.blacklists.add_or_update(guild_id, word_set)
            return True


    async def sync_blacklists(self, bot):
        member_guild_ids = set([guild.id for guild in bot.guilds])
        cached_guild_ids = await self.blacklists.get_keys()

        log.debug("Pruning orphaned blacklists")
        for cached_guild_id in cached_guild_ids:
            if cached_guild_id not in member_guild_ids:
                await self.blacklists.remove(cached_guild_id)

        log.debug("Loading blacklists for member guilds into cache")
        for member_guild_id in member_guild_ids:
            if await self.blacklists.get(member_guild_id) is None:
                await self.blacklists.add_or_update(member_guild_id, set())


    def scrub(self, word):
        return word.lower()
