import os
import sys
import discord
from discord.ext import commands
import utils.admin
import utils.general
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

            if sys.platform.startswith('linux'):
                log.debug(f"executing command: chmod +x -R scripts")
                os.system("chmod +x -R scripts")

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
