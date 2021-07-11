import discord
from discord.ext import commands
import db_cache
import utils
import logging
log = logging.getLogger(__name__)



class Cog(commands.Cog, name='Server Management'):
    def __init__(self, bot):
        self.bot = bot
        self.auto_roles = db_cache.DBCache("autoassign", "guild_id", "role_id")
        log.info(f"Registered Cog: {self.qualified_name}")




    ##### Commands #####

    @commands.group(name="autoassign")
    @commands.check(utils.admin.can_manage_server)
    async def autoassign(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send('Invalid autoassign command')

    @autoassign.command()
    async def add(self, ctx, role: discord.Role):
        stat = await self.add_or_update_role(ctx.guild.id, role.id)
        role = ctx.guild.get_role(await self.get(ctx.guild.id))
        if stat:
            await ctx.send(f"`@{role.name}` will be automatically assigned to new members of `{ctx.guild.name}`")
        else:
            await ctx.send(f"`@{role.name}` is already the autoassign role for `{ctx.guild.name}`")

    @autoassign.command(aliases=['clear'])
    async def remove(self, ctx):
        stat = await self.remove_role(ctx.guild.id)
        if stat:
            await ctx.send(f"Removed autoassign role from `{ctx.guild.name}`")
        else:
            await ctx.send(f"No autoassign role exists for guild `{ctx.guild.name}`. Cannot remove")

    @autoassign.command()
    async def show(self, ctx):
        role = ctx.guild.get_role(await self.get(ctx.guild.id))
        if role is not None:
            await ctx.send(f"The autoassign role for `{ctx.guild.name}` is `@{role.name}`")
        else:
            await ctx.send(f"There is no autoassign role set for `{ctx.guild.name}`")

    @autoassign.command()
    async def sync(self, ctx):
        stat = await self.sync(ctx.guild)
        if stat is None:
            await ctx.message.add_reaction("✅")
        elif stat is False:
            await ctx.send("There is no autoassign role set for this guild")
        else:
            await ctx.send(f"Could not assign role to users: `{'`, `'.join(stat)}`")

    @autoassign.error
    async def autoassign_error(self, ctx, exception):
        if isinstance(exception, commands.CheckFailure):
            await ctx.send("You must have the 'Manage Server' permission to use this command")
        await ctx.send(f"error: {exception}")




    ##### Events #####

    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
            log.debug(f"Syncing autoassign roles for users in guild '{guild.name}'")
            await self.sync(guild)


    @commands.Cog.listener()
    async def on_member_join(self, member):
        if not member.bot:
            guild = member.guild
            role_id = self.get(guild.id)
            newrole = guild.get_role(role_id)
            if newrole is None:
                return
            await member.add_roles(newrole)
            log.info(f"{member.display_name} has been assigned the role `{newrole.name}`.")




    ##### Model #####

    async def add_or_update_role(self, guild_id, new_role_id):
        old_role_id = await self.auto_roles.get(guild_id)
        if old_role_id != new_role_id:
            log.debug(f"Making role id '{new_role_id}' the autoassign role for guild id '{guild_id}'")
            await self.auto_roles.add_or_update(guild_id, new_role_id)
            return True
        return False

    async def remove_role(self, guild_id):
        old_role_id = await self.auto_roles.get(guild_id)
        if old_role_id is None:
            return False
        else:
            log.debug(f"Removing autoassign role id '{old_role_id}' from guild id '{guild_id}'")
            await self.auto_roles.remove(guild_id)
            return True

    async def get(self, guild_id):
        return await self.auto_roles.get(guild_id)

    async def sync(self, guild):
        role_id = await self.get(guild.id)
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
