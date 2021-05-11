import discord
from discord.ext import commands
import utils
import logging
import db
import math
import asyncio
log = logging.getLogger(__name__)

### TODO: make this bitch thread/async safe

class Cog(commands.Cog, name='Voting'):
    def __init__(self, bot):
        self.bot = bot
        log.info(f"Registered Cog: {self.qualified_name}")

    # class vars
    votes_in_progress = {}
    

    ### SETUP

    @commands.command()
    @commands.check(utils.is_owner)
    async def voterrole(self, ctx, *, new_role: discord.Role):
        old_role = get_voter_role(ctx.guild)
        
        sql_data = [["voting_role_id", new_role.id], ["guild_id", ctx.guild.id]]

        if(old_role.id == new_role.id):
            message = await ctx.send(f"`{new_role.name}` is already the voting role in `{ctx.guild.name}`")
        elif old_role is ctx.guild.default_role:
            db.insert("voting", sql_data)
            msg = f"Added voting role: `{get_voter_role(ctx).name}` in `{ctx.guild.name}`"
            log.info(msg)
            message = await ctx.send(msg)
        else:
            db.update("voting", sql_data)
            msg = f"Changed voting role from `{old_role.name}` to `{get_voter_role(ctx).name}`"
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
        message = await ctx.send(f"Removed voter role from `{ctx.guild.name}`\n`{get_voter_role(ctx).name}` can now vote.")
        #await utils.send_confirmation(ctx)
        #await message.delete(delay=30)



    ### VOTING

    @commands.command()
    @commands.check(utils.is_owner)
    async def votekick(self, ctx, *, member: discord.Member):
        voter_role = await get_voter_role(ctx.guild)
        num_votes = math.floor(len([voter for voter in voter_role.members if not voter.bot]) / 2) + 1

        embed = (discord.Embed(
            color=discord.Colour(utils.random_color()),
            title=f"Vote Kick:   5 minutes",
            description=f"""Voting to kick: {member.mention}
            Votes needed to win: **{num_votes}**
            {voter_role.mention} can vote"""
            )
            .set_thumbnail(url=member.avatar_url)
            .add_field(name="Yes", value=0)
            .add_field(name="No", value=0)
        )
        message = await ctx.send(embed = embed)
        await message.add_reaction("✅")
        await message.add_reaction("❌")
        
        await Vote.create(message, embed, num_votes)
        vote = self.votes_in_progress.get(message)

        # wait some time before ending
        await asyncio.sleep(100)
        if not vote.completed:
            vote.votefail

    @votekick.error
    async def status_error(self, ctx, exception):
        await ctx.send(f"error: {exception}")

    

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if reaction.message not in self.votes_in_progress or user is self.bot.user:
            return
        
        vote = self.votes_in_progress.get(reaction.message)

        if vote.voter_role not in user.roles:
            log.debug(f"removing reaction by user: {user.display_name} because they do not have role: {vote.voter_role.name}")
            await reaction.remove(user)
            return

        if reaction.emoji == "✅":
            await vote.voteyes(user)
        elif reaction.emoji == "❌":
            await vote.voteno(user)
        

    ## todo
    # make "vote object"
    # create it on start of vote
    # add users to list of "yes" or list of "no"
    # if user votes for no while already on yes list, remove them from yes list (remove reaction too)



### UTILS

# db functions aren't async and probably block
async def get_voter_role(guild):
    role_id = db.select("voting_role_id", "voting", "guild_id", guild.id)
    log.debug(f"received voting_role_id: {role_id} from sql query where guild_id = {guild.id}")
    if role_id is not None:
        return guild.get_role(role_id)
    else:
        return guild.default_role




class Vote:
    def __init__(self, message, voter_role, embed, votes_needed):
        self.message = message
        self.voter_role = voter_role
        self.embed = embed
        self.users_yes = set()
        self.users_no = set()
        self.completed = False
        self.votes_needed = votes_needed
        

    @classmethod
    async def create(self, message, embed, votes_needed):
        voter_role = await get_voter_role(message.guild)

        # Construc object, add it to list
        vote = Vote(message, voter_role, embed, votes_needed)
        Cog.votes_in_progress.update({message : vote})
        return vote


    async def voteyes(self, user):
        if user in self.users_yes:
            log.debug(f"{user.display_name} has already voted no")
            return
        elif user in self.users_no:
            log.debug(f"{user.display_name} has changed their vote from no to yes")
            self.users_no.remove(user)
            await self.message.remove_reaction("❌", user)
        self.users_yes.add(user)
        await self.update()

    async def voteno(self, user):
        if user in self.users_no:
            log.debug(f"{user.display_name} has already voted no")
            return
        if user in self.users_yes:
            log.debug(f"{user.display_name} has changed their vote from yes to no")
            self.users_yes.remove(user)
            await self.message.remove_reaction("✅", user)
        self.users_no.add(user)
        await self.update()


    async def update(self):
        self.embed.set_field_at(0, name="Yes", value=len(self.users_yes))
        self.embed.set_field_at(1, name="No", value=len(self.users_no))
        await self.message.edit(embed = self.embed)

    async def votepass(self):
        self.embed.title="Vote Kick:   Pass"
        self.embed.colordiscord.Colour(65280)
        self.message.edit(embed = self.embed)
        self.completed = True

    async def votefail(self):
        self.embed.title="Vote Kick:   Fail"
        self.embed.colordiscord.Colour(16711680)
        self.message.edit(embed = self.embed)
        self.completed = True
