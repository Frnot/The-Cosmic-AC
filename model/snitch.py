import db_cache
import logging
log = logging.getLogger(__name__)

hooked_channels = db_cache.DBCache("snitch", "guild_id", "hook_channel_id")
guild_invite_maps = {} # guild_id -> Invites[]



async def add_or_update_guild(self, guild, new_channel):
    old_channel_id = await hooked_channels.get(guild.id)

    await hooked_channels.add_or_update(guild.id, new_channel.id)
    await self.track_invites(guild)

    return (old_channel_id, new_channel.id)


async def remove_guild(self, guild):
    await hooked_channels.remove(guild.id)
    await self.untrack_invites(guild)



async def load_invite_maps(self, bot):
    for guild in bot.guilds:
        if await hooked_channels.get(guild.id) is not None:
            await self.track_invites(guild)


async def track_invites(self, guild):
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



async def notify(self, guild, message):
    channel_id = await hooked_channels.get(guild.id)
    if channel_id is not None:
        await guild.get_channel(channel_id).send(message)
