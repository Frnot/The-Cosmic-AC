from discord.ext import commands
import model.snitch
import time
import logging
log = logging.getLogger(__name__)



class Cog(commands.Cog, name='Snitch Events'):
    def __init__(self, bot):
        self.bot = bot
        log.info(f"Registered Cog: {self.qualified_name}")



    @commands.Cog.listener()
    async def on_ready(self):
        log.info("Generating invite tracking sets")
        time_start = time.perf_counter()
        model.snitch.load_invite_maps(self.bot)
        time_end = time.perf_counter()
        log.info(f"Generating invite tracking sets: completed in {time_end - time_start:0.6f} seconds")

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        model.snitch.untrack_invites(guild)


    @commands.Cog.listener()
    async def on_member_join(self, member):
        old_invite_map = self.guild_invite_maps.get(member.guild.id)
        new_invite_map = await self.track_invites(member.guild)
        if old_invite_map is not None:
            for invite_id in old_invite_map:
                if new_invite_map.get(invite_id) is not None and old_invite_map[invite_id].uses != new_invite_map[invite_id].uses:
                    invite_used = new_invite_map[invite_id]
                    log.info(f"({member.guild.member_count}) {member.display_name} has joined {member.guild.name} with invite {invite_used.code}")
                    await model.snitch.notify(member.guild, f"📈 ({member.guild.member_count}) {member.mention} (`{member.display_name}`) has joined with invite `{invite_used.code}`")
                    return
        
        log.info(f"({member.guild.member_count}) {member.display_name} has joined {member.guild.name}")
        await model.snitch.notify(member.guild, f"📈 ({member.guild.member_count}) {member.mention} (`{member.display_name}`) has joined")


    @commands.Cog.listener()
    async def on_member_remove(self, member):
        log.info(f"({member.guild.member_count}) {member.display_name} has left {member.guild.name}")
        await model.snitch.notify(member.guild, f"📉 ({member.guild.member_count}) {member.mention} (`{member.display_name}`) has left")
        # Get audit log entry and snitch on leave or kick and reason

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        ban = await guild.fetch_ban(user)
        log.info(f"{user.display_name} has been banned from {guild.name} reason: {ban.reason}")
        await model.snitch.notify(guild, f"{user.mention} (`{user.display_name}`) has been banned. reason: `{ban.reason}`")

    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):
        log.info(f"{user.display_name} has been unbanned from {guild.name}")
        await model.snitch.notify(guild, f"{user.mention} (`{user.display_name}`) has been unbanned")

    @commands.Cog.listener()
    async def on_invite_create(self, invite):
        log.info(f"{invite.inviter.display_name} has created an invite for {invite.guild.name} : {invite.url}")
        await model.snitch.notify(invite.guild, f"{invite.inviter.mention} (`{invite.inviter.display_name}`) has created an invite  : `{invite.url}`")
        await self.track_invites(invite.guild)

    @commands.Cog.listener()
    async def on_invite_delete(self, invite):
        log.info(f"invite {invite.url} for {invite.guild.name} has been deleted")
        await model.snitch.notify(invite.guild, f"invite `{invite.url}` has been deleted")
        await self.track_invites(invite.guild)
