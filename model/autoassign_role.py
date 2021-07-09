import db_cache
import discord
import logging
log = logging.getLogger(__name__)

auto_roles = db_cache.DBCache("autoassign", "guild_id", "role_id")


async def add_or_update_role(guild_id, new_role_id):
    old_role_id = await auto_roles.get(guild_id)
    if old_role_id != new_role_id:
        log.debug(f"Making role id '{new_role_id}' the autoassign role for guild id '{guild_id}'")
        await auto_roles.add_or_update(guild_id, new_role_id)
        return True
    return False

async def remove_role(guild_id):
    old_role_id = await auto_roles.get(guild_id)
    if old_role_id is None:
        return False
    else:
        log.debug(f"Removing autoassign role id '{old_role_id}' from guild id '{guild_id}'")
        await auto_roles.remove(guild_id)
        return True

async def get(guild_id):
    return await auto_roles.get(guild_id)

async def sync(guild):
    role_id = await get(guild.id)
    role = guild.get_role(role_id)
    if role is None:
        log.debug(f"Not syncing autoassign roles for guild '{guild.name}'. No autoassign role set")
        return False

    unassigned_members = []
    for member in guild.members:
        if not member.bot and role not in member.roles:
            try:
                await member.add_roles(role)
            except Exception as e:
                if isinstance(e, discord.errors.Forbidden):
                    log.debug(f"Cannot sync role '{role.name}' to user '{member.name}' in guild '{guild.name}' : '{e}'")
                unassigned_members.append(member.name)
                continue
            log.info(f"{member.display_name} has been assigned the role `{role.name}`.")
    return unassigned_members if unassigned_members else None
