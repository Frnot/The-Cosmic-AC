import discord
from discord.ext import commands
import utils
import logging
log = logging.getLogger(__name__)


class Cog(commands.Cog, name='Server Management'):
    def __init__(self, bot):
        self.bot = bot
        log.info(f"Registered Cog: {self.qualified_name}")

    # Event Listeners
    # Give every new member a role
    @commands.Cog.listener()
    async def on_member_join(self, member):
        role = member.guild.get_role(833019419805352007)
        await member.add_roles(role)
        log.info(f"{member.display_name} has been assigned the role `people`.")