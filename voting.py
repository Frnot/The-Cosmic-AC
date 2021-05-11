import discord
from discord.ext import commands
import utils
import logging
import db
import math
log = logging.getLogger(__name__)

### TODO: make this bitch thread/async safe

class Cog(commands.Cog, name='Voting'):
    def __init__(self, bot):
        self.bot = bot
        log.info(f"Registered Cog: {self.qualified_name}")

    # class vars
    votes_in_progress = []
    

    ### SETUP

    @commands.command()
    @commands.check(utils.is_owner)
    async def voterrole(self, ctx, *, new_role: discord.Role):
        old_role = self.get_voter_role(ctx.guild)
        
        sql_data = [["voting_role_id", new_role.id], ["guild_id", ctx.guild.id]]

        if(old_role.id == new_role.id):
            message = await ctx.send(f"`{new_role.name}` is already the voting role in `{ctx.guild.name}`")
        elif old_role is ctx.guild.default_role:
            db.insert("voting", sql_data)
            msg = f"Added voting role: `{self.get_voter_role(ctx).name}` in `{ctx.guild.name}`"
            log.info(msg)
            message = await ctx.send(msg)
        else:
            db.update("voting", sql_data)
            msg = f"Changed voting role from `{old_role.name}` to `{self.get_voter_role(ctx).name}`"
            log.info(msg)
            message = await ctx.send(msg)
        #await utils.send_confirmation(ctx)
        #await message.delete(delay=30)


    @commands.command()
    @commands.check(utils.is_owner)
    async def novoterrole(self, ctx):
        sql_data = ["guild_id", ctx.guild.id]
        db.delete("voting", sql_data)
        log.info(f"Removed voter role from `{ctx.guild.name}`")
        message = await ctx.send(f"Removed voter role from `{ctx.guild.name}`\n`{self.get_voter_role(ctx).name}` can now vote.")
        #await utils.send_confirmation(ctx)
        #await message.delete(delay=30)



    ### VOTING

    @commands.command()
    @commands.check(utils.is_owner)
    async def votekick(self, ctx, *, member: discord.Member):
        voter_role = self.get_voter_role(ctx.guild)
        num_votes = math.floor(len([voter for voter in voter_role.members if not voter.bot]) / 2) + 1

        embed = (discord.Embed(
            color=discord.Colour(utils.random_color()),
            title=f"Vote Kick:   5 minutes",
            description=f"""Voting to kick: {member.mention}
            Votes needed to win: **{num_votes}**
            {voter_role.mention} can vote"""
            )
            .set_thumbnail(url=member.avatar_url)
            .add_field(name="Yes", value=1)
            .add_field(name="No", value=2)
        )
        message = await ctx.send(embed = embed)
        await message.add_reaction("✅")
        await message.add_reaction("❌")
        
        self.votes_in_progress.append(message)
        # wait some time before ending


    @votekick.error
    async def status_error(self, ctx, exception):
        await ctx.send(f"error: {exception}")

    

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if reaction.message not in self.votes_in_progress:
            return

        voter_role = self.get_voter_role(reaction.message.guild)
        if voter_role not in user.roles and user is not self.user:
            log.debug(f"removing reaction by user: {user.display_name} because they do not have role: {voter_role.name}")
            await reaction.remove(user)
            return

        embed = reaction.message.embeds[0]
        if reaction.emoji == "✅":
            embed.set_field_at(0, name="Yes", value=99)
            await reaction.message.edit(embed = embed)
        elif reaction.emoji == "❌":
            embed.set_field_at(1, name="Yes", value=99)
            await reaction.message.edit(embed = embed)
        

    ## todo
    # make "vote object"
    # create it on start of vote
    # add users to list of "yes" or list of "no"
    # if user votes for no while already on yes list, remove them from yes list (remove reaction too)

    ### UTILS

    def get_voter_role(self, guild):
        role_id = db.select("voting_role_id", "voting", "guild_id", guild.id)
        log.debug(f"received voting_role_id: {role_id} from sql query where guild_id = {guild.id}")
        if role_id is not None:
            return guild.get_role(role_id)
        else:
            return guild.default_role
