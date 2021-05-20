from discord.ext import commands
import logging
log = logging.getLogger(__name__)


class Cog(commands.Cog, name='Server Management'):
    def __init__(self, bot):
        self.bot = bot
        log.info(f"Registered Cog: {self.qualified_name}")

    
    ## Give every new member a role
    @commands.Cog.listener()
    async def on_member_join(self, member):
        if not member.bot:
            guild = member.guild
            newrole = guild.get_role(833019117992542248)
            await member.add_roles(newrole)
            log.info(f"{member.display_name} has been assigned the role `{newrole.name}`.")

    @commands.command()
    async def roleup(self, ctx):
        newrole = ctx.guild.get_role(833019117992542248)
        for member in ctx.guild.members:
            if not member.bot and newrole not in member.roles:
                await member.add_roles(newrole)
                log.info(f"{member.display_name} has been assigned the role `{newrole.name}`.")
        log.info("command: roleup finished.")