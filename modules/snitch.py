from discord.ext import commands
from database.cache import Cache
import time
import utils.admin
import logging
log = logging.getLogger(__name__)



class Cog(commands.Cog, name='Snitch'):
    def __init__(self, bot):
        self.bot = bot
        self.hooked_channels = Cache("snitch", "guild_id", "hook_channel_id")
        self.guild_invite_maps = {} # guild_id -> Invites[]
        log.info(f"Registered Cog: {self.qualified_name}")




    ##### Commands #####

    @commands.command()
    @commands.check(utils.admin.is_server_owner)
    async def snitch(self, ctx):
        stat = await self.add_or_update_guild(ctx.guild, ctx.channel)
        old_channel_id, new_channel_id = stat

        if(old_channel_id == new_channel_id):
            await ctx.send("I'm already snitching in this channel")
        elif old_channel_id is None:
            log.info(f"started snitching on '{ctx.guild.name}'")
            await ctx.send(f"Will snitch on `{ctx.guild.name}` in `#{ctx.channel.name}`")
        else:
            log.info(f"changed snitch hooked channel in '{ctx.guild.name}' from '{self.bot.get_channel(old_channel_id)}' to '{ctx.channel.name}'")
            await ctx.send(f"Moved `{ctx.guild.name}` snitch channel to `#{ctx.channel.name}`")

    @snitch.error
    async def snitch_error(self, ctx, exception):
        await ctx.send(f"error: {exception}")


    @commands.command()
    @commands.check(utils.admin.is_server_owner)
    async def stopsnitching(self, ctx):
        await self.remove_guild(ctx.guild)
        log.info(f"Removed snitch channel from '{ctx.guild.name}'")
        await ctx.send(f"Will no longer snitch on `{ctx.guild.name}`")

    @stopsnitching.error
    async def stopsnitching_error(self, ctx, exception):
        await ctx.send(f"error: {exception}")




    ##### Events #####

    @commands.Cog.listener()
    async def on_ready(self):
        log.info("Generating invite tracking sets")
        time_start = time.perf_counter()
        await self.load_invite_maps(self.bot)
        time_end = time.perf_counter()
        log.info(f"Generating invite tracking sets: completed in {time_end - time_start:0.6f} seconds")

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        await self.untrack_invites(guild)

    @commands.Cog.listener()
    async def on_invite_create(self, invite):
        log.info(f"{invite.inviter.display_name} has created an invite for {invite.guild.name} : {invite.url}")
        await self.notify(invite.guild, f"{invite.inviter.mention} (`{invite.inviter.display_name}`) has created an invite  : `{invite.url}`")
        #TODO optimize this
        await self.track_invites(invite.guild)

    @commands.Cog.listener()
    async def on_invite_delete(self, invite):
        log.info(f"invite {invite.url} for {invite.guild.name} has been deleted")
        await self.notify(invite.guild, f"invite `{invite.url}` has been deleted")
        #TODO optimize this
        await self.track_invites(invite.guild)


    # TODO: put this logic in model
    @commands.Cog.listener()
    async def on_member_join(self, member):
        old_invite_map = await self.get_invite_map(member.guild)
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
        # Get audit log entry and snitch on leave or kick and reason

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        ban = await guild.fetch_ban(user)
        log.info(f"{user.display_name} has been banned from {guild.name} reason: {ban.reason}")
        await self.notify(guild, f"{user.mention} (`{user.display_name}`) has been banned. reason: `{ban.reason}`")
        
        # TODO: check for this on startup too
        invite_map = await self.get_invite_map(guild)
        if invite_map is not None:
            log.debug(f"Deleting invites from '{user.display_name}' in guild '{guild.name}'")
            for invite in invite_map.values():
                if invite.inviter == user:
                    await invite.delete(reason="Invite creator has been banned")
                    log.info(f"{user.display_name}'s invite {invite.url} for {guild.name} has been deleted")
        else:
            log.debug(f"Cannot delete banned member's invites. Invites are not being tracked for guild '{guild.name}'")

    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):
        log.info(f"{user.display_name} has been unbanned from {guild.name}")
        await self.notify(guild, f"{user.mention} (`{user.display_name}`) has been unbanned")




    ##### Model #####

    async def add_or_update_guild(self, guild, new_channel):
        old_channel_id = await self.hooked_channels.get(guild.id)

        await self.hooked_channels.add_or_update(guild.id, new_channel.id)
        await self.track_invites(guild)

        return (old_channel_id, new_channel.id)


    async def remove_guild(self, guild):
        await self.hooked_channels.remove(guild.id)
        await self.untrack_invites(guild)


    async def load_invite_maps(self, bot):
        for guild in bot.guilds:
            await self.track_invites(guild)


    async def track_invites(self, guild):
        if await self.hooked_channels.get(guild.id) is None:
            return
        
        if not guild.get_member(self.bot.user.id).guild_permissions.manage_guild:
            log.error(f"Missing permission 'manage_guild' in guild '{guild.name}. Cannot track invites.")
            return None
        
        log.debug(f"Tracking invites for guild: {guild.name}")
        invite_set = await guild.invites()
        invite_map = {}
        for invite in invite_set:
            invite_map[invite.id] = invite
        self.guild_invite_maps[guild.id] = invite_map
        return invite_map


    async def untrack_invites(self, guild):
        log.debug(f"Untracking invites for guild: {guild.name}")
        self.guild_invite_maps.pop(guild.id)


    async def get_invite_map(self, guild):
        return self.guild_invite_maps.get(guild.id)


    async def notify(self, guild, message):
        channel_id = await self.hooked_channels.get(guild.id)
        if channel_id is not None:
            await guild.get_channel(channel_id).send(message)
