from discord.ext import commands
from model import blacklist
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
        await blacklist.sync_blacklists(self.bot)
        log.info("Done.")

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.author.bot:
            word_set = await blacklist.get(message.guild.id)
            if word_set is not None:
                for word in word_set:
                    if word in message.content.lower():
                        await message.delete()
                        log.info(f"Removed message \"{message.content}\" from {message.author.display_name} in #{message.channel.name}@{message.guild.name} - contained blacklisted word: \"{word}\"")

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        await self.on_message(after)
