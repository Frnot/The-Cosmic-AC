import discord
from discord.ext import commands
from model import blacklist
import time
import logging
log = logging.getLogger(__name__)

from fuzzysearch import find_near_matches



class Cog(commands.Cog, name='Admin Events'):
    def __init__(self, bot):
        self.bot = bot
        log.info(f"Registered Cog: {self.qualified_name}")




    ## Blacklist
    @commands.Cog.listener()
    async def on_ready(self):
        log.info("Loading blacklist database into cache")
        time_start = time.perf_counter()
        await blacklist.sync_blacklists(self.bot)
        time_end = time.perf_counter()
        log.info(f"Loading blacklist database into cache: complete in {time_end - time_start:0.6f} seconds")

    # Optimize when necessary (guild count is sufficiently large)
    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        log.info("Creating empty blacklist for new guild")
        time_start = time.perf_counter()
        await blacklist.sync_blacklists(self.bot)
        time_end = time.perf_counter()
        log.info(f"Creating empty blacklist for new guild: complete in {time_end - time_start:0.6f} seconds")

    # Optimize when necessary (guild count is sufficiently large)
    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        log.info("Removing blacklist for expired guild")
        time_start = time.perf_counter()
        await blacklist.sync_blacklists(self.bot)
        time_end = time.perf_counter()
        log.info(f"Removing blacklist for expired guild: complete in {time_end - time_start:0.6f} seconds")

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.author.bot:
            # perform a shallow copy on word_set to avoid race condition
            word_set = set(await blacklist.get(message.guild.id))

            test_message = message.content.replace(" ", "").lower()

            for word in word_set:
                l_dist = 3
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
