import discord
from discord.ext import commands
import utils
import logging
log = logging.getLogger(__name__)


class Cog(commands.Cog, name='Snitch'):
    # guild.id -> channel
    guild_channels=dict()

    def __init__(self, bot):
        self.bot = bot
        log.info(f"Registered Cog: {self.qualified_name}")

    async def snitch(self, guild, message):
        if (guild.id in self.guild_channels):
            await self.guild_channels[guild.id].send(message)
        log.info(message)

    @commands.command()
    @commands.check(utils.is_owner)
    async def creep(self, ctx):
        if(ctx.guild.id not in self.guild_channels):
            await ctx.send("I'm already snitchin on this server")
        self.guild_channels[ctx.guild.id] = ctx.channel

    @commands.Cog.listener()
    async def on_member_join(self, member):
        await self.snitch(member.guild, f"{member} has joined '{member.guild.name}'")

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        await self.snitch(member.guild, f"{member} has left '{member.guild.name}'")

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        await self.snitch(guild, f"{user} has been banned from '{guild.name}'")

    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):
        await self.snitch(guild, f"{user} has been unbanned from `{guild.name}`")

    @commands.Cog.listener()
    async def on_invite_create(self, invite):
        await self.snitch(invite.guild, f"`{invite.inviter}` has created an invite for `{invite.guild.name}`")

    @commands.Cog.listener()
    async def on_invite_delete(self, invite):
        await self.snitch(invite.guild, f"an invite for `{invite.guild.name}`` has been deleted")

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        await self.snitch(member.guild, f"{member}'s voice state has changed in channel `#{after.channel.name}` in guild `{after.channel.guild.name}`")
