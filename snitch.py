import discord
from discord.ext import commands
import utils
import db
import logging
log = logging.getLogger(__name__)


class Cog(commands.Cog, name='Snitch'):
    def __init__(self, bot):
        self.bot = bot
        log.info(f"Registered Cog: {self.qualified_name}")
        # load lookup table from db here if necessary

    # Commands
    @commands.command()
    @commands.check(utils.is_owner)
    async def snitch(self, ctx):
        channel_id = db.select("hook_channel_id", "snitch", "guild_id", ctx.guild.id)
        log.debug(f"received channel_id: {channel_id} from sql query")
        if(ctx.channel.id == channel_id):
            await ctx.send("I'm already snitching in this channel")
        elif channel_id is not None:
            db.update("snitch", "(guild_id, hook_channel_id)", f"({ctx.guild.id}, {ctx.channel.id})")
            log.info(f"changed snitch hooked channel from {self.bot.get_channel(channel_id)} to {ctx.channel.name}")
            await ctx.send(f"Moved `{ctx.guild.name}` snitch channel to `#{ctx.channel.name}`")
        else:
            db.insert("snitch", "(guild_id, hook_channel_id)", f"({ctx.guild.id}, {ctx.channel.id})")
            log.info(f"started snitching on {ctx.guild.name}")
            await ctx.send(f"Will snitch on `{ctx.guild.name}` in `#{ctx.channel.name}`")


    # Event Listeners
    @commands.Cog.listener()
    async def on_member_join(self, member):
        await self.notify(member.guild, f"{member.display_name} has joined `{member.guild.name}`")

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        await self.notify(member.guild, f"{member.mention} (`{member.display_name}`) has left `{member.guild.name}`")

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        await self.notify(guild, f"{user.mention} (`{user.display_name}`) has been banned from `{guild.name}`")

    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):
        await self.notify(guild, f"{user.mention} (`{user.display_name}`) has been unbanned from `{guild.name}`")

    @commands.Cog.listener()
    async def on_invite_create(self, invite):
        await self.notify(invite.guild, f"`{invite.inviter.display_name}` has created an invite for `{invite.guild.name}`")

    @commands.Cog.listener()
    async def on_invite_delete(self, invite):
        await self.notify(invite.guild, f"an invite for `{invite.guild.name}` has been deleted")

    #@commands.Cog.listener()
    #async def on_voice_state_update(self, member, before, after):
        #await self.notify(member.guild, f"{member.display_name}'s voice state has changed in channel `#{after.channel.name}` in guild `{after.channel.guild.name}`")


    # Module Functions
    async def notify(self, guild, message):
        log.info(message)
        channel_id = db.select("hook_channel_id", "snitch", "guild_id", guild.id)
        log.debug(f"received channel_id: {channel_id} from sql query")
        if channel_id is not None:
            await guild.get_channel(channel_id).send(message)
        else:
            log.debug(f"Event fired but guild {guild} was not subscribed")
