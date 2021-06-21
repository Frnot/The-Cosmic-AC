import os
import sys
import discord
from discord.ext import commands
import utils.admin
import utils.general
from model import prefix, blacklist, snitch
import logging
log = logging.getLogger(__name__)

restart = False

class Cog(commands.Cog, name='Admin Commands'):
    def __init__(self, bot):
        self.bot = bot
        log.info(f"Registered Cog: {self.qualified_name}")



    # Leave server
    @commands.command()
    @commands.is_owner()
    async def leave(self, ctx):
        log.info(f"Recieved leave command in guild {ctx.guild.name}")
        await ctx.message.add_reaction("✅")
        await ctx.guild.leave()

    @leave.error
    async def leave_error(self, ctx, exception):
        if isinstance(exception, commands.NotOwner):
            await ctx.send("You do not have permission to use this command")
        else:
            await ctx.send(f"error: {exception}")



    # Shutdown
    @commands.command()
    @commands.is_owner()
    async def die(self, ctx):
        log.info("Received shutdown command")
        await ctx.message.add_reaction("✅")
        await ctx.bot.close()

    @die.error
    async def shutdown_error(self, ctx, exception):
        if isinstance(exception, commands.NotOwner):
            await ctx.send("You do not have permission to use this command")
        else:
            await ctx.send(f"error: {exception}")



    # Install Updates
    @commands.command()
    @commands.is_owner()
    async def update(self, ctx):
        global restart
        restart = True

        async with ctx.channel.typing():
            await ctx.send("Updating...")
            log.info("Running Updates")

            log.debug("executing command: git stash")
            os.system("git stash")

            log.debug("executing command: git pull")
            os.system("git pull")

            log.debug(f"executing command: \"{sys.executable}\" -m pip install .")
            os.system(f"\"{sys.executable}\" -m pip install .")

            log.info("Updates done. Restarting main process")

        await ctx.bot.close()

    @update.error
    async def update_error(self, ctx, exception):
        if isinstance(exception, commands.NotOwner):
            await ctx.send("You do not have permission to use this command")
        else:
            await ctx.send(f"error: {exception}")



    # Set status
    @commands.command()
    @commands.is_owner()
    async def status(self, ctx, action: utils.general.to_lower, status):
        if action == "playing":
            actiontype = discord.ActivityType.playing
        elif action == "streaming":
            actiontype = discord.ActivityType.streaming
        elif action in ("listening", "listening to"):
            actiontype = discord.ActivityType.listening
        elif action == "watching":
            actiontype = discord.ActivityType.watching
        elif action in ("competing", "competing in"):
            actiontype = discord.ActivityType.competing

        await self.bot.change_presence(activity=discord.Activity(name=status, type=actiontype))

        log.info(f"setting status to {actiontype.name} `{status}`")
        await utils.general.send_confirmation(ctx)

    @status.error
    async def status_error(self, ctx, exception):
        if isinstance(exception, commands.NotOwner):
            await ctx.send("You do not have permission to use this command")
        else:
            await ctx.send(f"error: {exception}")



    # Change per-guild command prefix
    @commands.command()
    @commands.check(utils.admin.is_server_owner)
    async def prefix(self, ctx, new_prefix=None):
        if new_prefix is None:
            current_prefix = await prefix.get(ctx.guild.id)
            await ctx.send(f"Command prefix: `{current_prefix}`")
            return
        elif new_prefix == "reset":
            log.info(f"Removing custom command prefix for guild '{ctx.guild.name}'")
            await prefix.remove(ctx.guild.id)
        else:
            log.info(f"Changing custom command prefix for guild '{ctx.guild.name}'")
            await prefix.add_or_update(ctx.guild.id, new_prefix)
        
        new_prefix = await prefix.get(ctx.guild.id)
        await ctx.send(f"Command prefix for {ctx.guild.name} is now `{new_prefix}`")

    @prefix.error
    async def prefix_error(self, ctx, exception):
        if isinstance(exception, commands.NotOwner):
            await ctx.send("You do not have permission to use this command")
        else:
            await ctx.send(f"error: {exception}")



    # Blacklist words
    @commands.group()
    @commands.check(utils.admin.is_server_owner)
    async def blacklist(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send('Invalid blacklist command')

    @blacklist.command()
    async def add(self, ctx, *args):
        added, existing = await blacklist.add_words(ctx.guild.id, args)
        if added:
            await ctx.send(f"Added `{'`, `'.join(added)}` to blacklist")
        if existing:
            await ctx.send(f"`{'`, `'.join(existing)}` already in blacklist")

    @blacklist.command()
    async def remove(self, ctx, *args):
        removed, not_exist = await blacklist.remove_words(ctx.guild.id, args)
        if removed:
            await ctx.send(f"Removed `{'`, `'.join(removed)}` from blacklist")
        if not_exist:
            await ctx.send(f"Blacklist does not contain `{'`, `'.join(not_exist)}`")

    @blacklist.command()
    async def clear(self, ctx):
        stat = await blacklist.clear_blacklist(ctx.guild.id)
        if stat is None:
            await ctx.send(f"There are no blacklisted words in this server")
        else:
            await ctx.send(f"Cleared blacklisted words for `{ctx.guild.name}`")

    @blacklist.command()
    async def show(self, ctx):
        wordlist = await blacklist.get(ctx.guild.id)
        if not wordlist:
            message = "There are no blacklisted words in this server"
        else:
            message = f"Blacklisted words: `{'`, `'.join(wordlist)}`"
        await ctx.send(message)

    @blacklist.error
    async def blacklist_error(self, ctx, exception):
        await ctx.send(f"error: {exception}")




    # Snitch
    @commands.command()
    @commands.check(utils.admin.is_server_owner)
    async def snitch(self, ctx):
        stat = await snitch.add_or_update_guild(ctx.guild, ctx.channel)
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
        await snitch.remove_guild(ctx.guild)
        log.info(f"Removed snitch channel from '{ctx.guild.name}'")
        await ctx.send(f"Will no longer snitch on `{ctx.guild.name}`")

    @stopsnitching.error
    async def stopsnitching_error(self, ctx, exception):
        await ctx.send(f"error: {exception}")