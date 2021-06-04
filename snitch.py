import discord
from discord.ext import commands
import utils.admin
import db
import logging
log = logging.getLogger(__name__)


class Cog(commands.Cog, name='Snitch'):
    guild_invite_maps = {} # guild_id -> Invite
    
    def __init__(self, bot):
        self.bot = bot
        log.info(f"Registered Cog: {self.qualified_name}")

    @commands.Cog.listener()
    async def on_ready(self):
        log.info("Generating invite tracking sets")
        for guild in self.bot.guilds:
            await self.track_invites(guild)



    # Commands
    @commands.command()
    @commands.check(utils.admin.is_server_owner)
    async def snitch(self, ctx):
        channel_id = await db.select("hook_channel_id", "snitch", "guild_id", ctx.guild.id)
        log.debug(f"received channel_id: {channel_id} from sql query where guild_id = {ctx.guild.id}")

        sql_data = [["guild_id", ctx.guild.id], ["hook_channel_id", ctx.channel.id]]
        
        if(ctx.channel.id == channel_id):
            await ctx.send("I'm already snitching in this channel")
        elif channel_id is not None:
            await db.update("snitch", sql_data)
            log.info(f"changed snitch hooked channel from {self.bot.get_channel(channel_id)} to {ctx.channel.name}")
            await ctx.send(f"Moved `{ctx.guild.name}` snitch channel to `#{ctx.channel.name}`")
        else:
            await db.insert("snitch", sql_data)
            log.info(f"started snitching on {ctx.guild.name}")
            await ctx.send(f"Will snitch on `{ctx.guild.name}` in `#{ctx.channel.name}`")



    @commands.command()
    @commands.check(utils.admin.is_server_owner)
    async def stopsnitching(self, ctx):
        sql_data = ["guild_id", ctx.guild.id]
        await db.delete("snitch", sql_data)
        log.info(f"Removed snitch channel from {ctx.guild.name}")
        await ctx.send(f"Will no longer snitch on `{ctx.guild.name}`")



    # Event Listeners
    @commands.Cog.listener()
    async def on_member_join(self, member):
        old_invite_map = self.guild_invite_maps.get(member.guild.id)
        new_invite_map = await self.track_invites(member.guild)
        if old_invite_map is not None:
            for invite_id in old_invite_map:
                if new_invite_map.get(invite_id) is not None and old_invite_map[invite_id].uses != new_invite_map[invite_id].uses:
                    invite_used = new_invite_map[invite_id]
                    log.info(f"({member.guild.member_count}) {member.display_name} has joined {member.guild.name} with invite {invite_used.code}")
                    await self.notify(member.guild, f"📈 ({member.guild.member_count}) {member.mention} (`{member.display_name}`) has joined with invite `{invite_used.code}`")
                    return
        
        log.info(f"({member.guild.member_count}) {member.display_name} has joined {member.guild.name}")
        await self.notify(member.guild, f"📈 ({member.guild.member_count}) {member.mention} (`{member.display_name}`) has joined")

        

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        log.info(f"({member.guild.member_count}) {member.display_name} has left {member.guild.name}")
        await self.notify(member.guild, f"📉 ({member.guild.member_count}) {member.mention} (`{member.display_name}`) has left")

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        ban = await guild.fetch_ban(user)
        log.info(f"{user.display_name} has been banned from {guild.name} reason: {ban.reason}")
        await self.notify(guild, f"{user.mention} (`{user.display_name}`) has been banned from `{guild.name}` reason: `{ban.reason}`")

    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):
        log.info(f"{user.display_name} has been unbanned from {guild.name}")
        await self.notify(guild, f"{user.mention} (`{user.display_name}`) has been unbanned")

    @commands.Cog.listener()
    async def on_invite_create(self, invite):
        log.info(f"{invite.inviter.display_name} has created an invite for {invite.guild.name} : {invite.url}")
        await self.notify(invite.guild, f"{invite.inviter.mention} (`{invite.inviter.display_name}`) has created an invite  : `{invite.url}`")
        await self.track_invites(invite.guild)

    @commands.Cog.listener()
    async def on_invite_delete(self, invite):
        log.info(f"invite {invite.url} for {invite.guild.name} has been deleted")
        await self.notify(invite.guild, f"invite `{invite.url}` has been deleted")
        await self.track_invites(invite.guild)



    # Module Functions
    async def track_invites(self, guild):
        if not guild.get_member(self.bot.user.id).guild_permissions.manage_guild:
            return None
        
        log.debug(f"Tracking invites for guild: {guild.name}")
        invite_set = await guild.invites()
        invite_map = {}
        for invite in invite_set:
            invite_map[invite.id] = invite
        self.guild_invite_maps[guild.id] = invite_map
        return invite_map


    async def notify(self, guild, message):
        channel_id = await db.select("hook_channel_id", "snitch", "guild_id", guild.id)
        log.debug(f"received channel_id: {channel_id} from sql query")
        if channel_id is not None:
            await guild.get_channel(channel_id).send(message)
        else:
            log.debug(f"Event fired but guild {guild} was not subscribed")
