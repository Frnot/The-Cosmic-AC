# Module contains coroutines that fire whenmemebers of a server take certain actions
import discord
from discord.ext import commands
import logging
log = logging.getLogger(__name__)


class Cog(commands.Cog, name='Snitch'):
    def __init__(self, bot):
        self.bot = bot
        log.info(f"Registered Cog: {self.qualified_name}")

    async def snitch(self, message):
        user = self.bot.get_user(175786263201185792)
        dm = user.dm_channel
        if dm == None:
            dm = await user.create_dm()
        await dm.send(message)
        log.info(message)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        await self.snitch(f"{member} has joined {member.guild.name}")

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        await self.snitch(f"{member} has left {member.guild.name}")

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        await self.snitch(f"{user} has been banned from {guild}")

    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):
        await self.snitch(f"{user} has been unbanned from {guild}")

    @commands.Cog.listener()
    async def on_invite_create(self, invite):
        await self.snitch(f"{invite.inviter} has created an invite for {invite.guild.name}")

    @commands.Cog.listener()
    async def on_invite_delete(self, invite):
        await self.snitch(f"an invite for {invite.guild.name} has been deleted")

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        await self.snitch(f"{member}'s voice state has changed in channel {after.channel.name} in guild {after.channel.guild.name}")
