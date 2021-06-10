from discord.ext import commands
from model import blacklist
import time
import logging
log = logging.getLogger(__name__)

class Cog(commands.Cog, name='General commands'):
    def __init__(self, bot):
        self.bot = bot
        log.info(f"Registered Cog: {self.qualified_name}")




    # Blacklist
    @commands.Cog.listener()
    async def on_ready(self):
        log.info("Loading blacklist database into cache")
        time_start = time.perf_counter()
        await blacklist.sync_blacklists(self.bot)
        time_end = time.perf_counter()
        log.info(f"Done. took {time_end - time_start:0.4f} seconds")

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        log.info("Creating empty blacklist for new guild")
        await blacklist.sync_blacklists(self.bot)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        log.info("Removing blacklist for expired guild")
        await blacklist.sync_blacklists(self.bot)

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.author.bot:
            # perform a shallow copy on word_set to avoid race condition
            word_set = set(await blacklist.get(message.guild.id))
            
            test_message = message.content.lower()
            if word_set is not None:
                for word in word_set:
                    if word in test_message:
                        await message.delete()
                        log.info(f"Removed message \"{message.content}\" from {message.author.display_name} in #{message.channel.name}@{message.guild.name} - contained blacklisted word: \"{word}\"")

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        await self.on_message(after)
