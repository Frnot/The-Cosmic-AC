import os
import sys
import discord
from discord.ext import commands
import utils.admin
import utils.general
from model import prefix, blacklist
import logging
log = logging.getLogger(__name__)

restart = False

class Cog(commands.Cog, name='General commands'):
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
    @commands.is_owner()
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




    # Blacklist words
    @commands.command()
    @commands.check(utils.admin.is_server_owner)
    async def blacklist(self, ctx, *args):
        guild_id = ctx.guild.id

        if len(args) < 1:
            return #error

        if args[0].lower() == "add":
            if len(args) < 2:
                return #error
            else:
                await blacklist.add_word(guild_id, args[1])
                await ctx.send(f"Added `{args[1]}` to blacklist")

        elif args[0].lower() == "remove":
            if len(args) < 2:
                return #error
            else:
                stat = await blacklist.remove_word(guild_id, args[1])
                if stat:
                    await ctx.send(f"Removed `{args[1]}` from blacklist")
                else:
                    await ctx.send(f"Blacklist does not contain `{args[1]}`")

        elif args[0].lower() == "clear":
            stat = await blacklist.clear_blacklist(guild_id)
            if stat is None:
                await ctx.send(f"There are no blacklisted words in this server")
            else:
                await ctx.send(f"Cleared blacklisted words for `{ctx.guild.name}`")

        elif args[0].lower() == "show":
            list = await blacklist.get(guild_id)
            if not list:
                message = "There are no blacklisted words in this server"
            else:
                message = f"Blacklisted words: `{'`, `'.join(list)}`"
            await ctx.send(message)


    @blacklist.error
    async def blacklist_error(self, ctx, exception):
        if isinstance(exception, commands.NotOwner):
            await ctx.send("You do not have permission to use this command")
        else:
            await ctx.send(f"error: {exception}")