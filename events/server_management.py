from discord.ext import commands
from model import autoassign_role
import logging
log = logging.getLogger(__name__)



class Cog(commands.Cog, name='Server Management'):
    def __init__(self, bot):
        self.bot = bot
        log.info(f"Registered Cog: {self.qualified_name}")


    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
            log.debug(f"Syncing autoassign roles for users in guild '{guild.name}'")
            await autoassign_role.sync(guild)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if not member.bot:
            guild = member.guild
            role_id = autoassign_role.get(guild.id)
            newrole = guild.get_role(role_id)
            if newrole is None:
                return
            await member.add_roles(newrole)
            log.info(f"{member.display_name} has been assigned the role `{newrole.name}`.")
