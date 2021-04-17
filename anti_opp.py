import discord
from discord.ext import commands
import utils
import db
import logging
log = logging.getLogger(__name__)


class Cog(commands.Cog, name='Anti Opp'):
    def __init__(self, bot):
        self.bot = bot
        log.info(f"Registered Cog: {self.qualified_name}")
        # load lookup table from db here if necessary

    # Event Listeners
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.find("discord.com/invite") != -1:
            await message.delete()
            log.info(f"{message.author.display_name}'s discord invite link has been deleted.')