import discord
from discord.ext import commands
import utils.admin
import utils.general
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
    @commands.check(utils.admin.is_owner)
    async def voterrole(self, ctx, *, new_role: discord.Role):
        old_role = get_voter_role(ctx.guild)
        
        sql_data = [["voting_role_id", new_role.id], ["guild_id", ctx.guild.id]]

        if(old_role.id == new_role.id):
            message = await ctx.send(f"`{new_role.name}` is already the voting role in `{ctx.guild.name}`")
        elif old_role is ctx.guild.default_role:
            db.insert("voting", sql_data)
            msg = f"Added voting role: `{get_voter_role(ctx.guild).name}` in `{ctx.guild.name}`"
            log.info(msg)
            message = await ctx.send(msg)
        else:
            db.update("voting", sql_data)
            msg = f"Changed voting role from `{old_role.name}` to `{get_voter_role(ctx.guild).name}`"
            log.info(msg)
            message = await ctx.send(msg)
        #await utils.send_confirmation(ctx)
        #await message.delete(delay=30)


    @commands.command()
    @commands.check(utils.admin.is_owner)
    async def novoterrole(self, ctx):
        sql_data = ["guild_id", ctx.guild.id]
        db.delete("voting", sql_data)
        log.info(f"Removed voter role from `{ctx.guild.name}`")
        message = await ctx.send(f"Removed voter role from `{ctx.guild.name}`\n`{get_voter_role(ctx.guild).name}` can now vote.")
        #await utils.send_confirmation(ctx)
        #await message.delete(delay=30)



    ### VOTING

    def can_vote(ctx):
        return get_voter_role(ctx.guild) in ctx.author.roles or ctx.author == ctx.guild.owner

    @commands.command()
    @commands.check(can_vote)
    async def votekick(self, ctx, *, member: discord.Member):
        # TODO check that bot has permission to kick the target member
        
        vote = await Vote.create(ctx, member)
        await vote.message.pin()

        # wait some time before ending
        await asyncio.sleep(600)
        if not vote.completed:
            await vote.votetime()

    @votekick.error
    async def status_error(self, ctx, exception):
        await ctx.send(f"error: {exception}")

    

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if user == self.bot.user:
            log.debug("Returning because bot reacted")
            return
        if reaction.message not in self.votes_in_progress:
            log.debug("Returning because reacted message is not a vote")
            return
        
        vote = self.votes_in_progress.get(reaction.message)

        if user not in vote.voters:
            log.debug(f"removing reaction by user: {user.display_name} because they are not in the list of allowed voters")
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
def get_voter_role(guild):
    role_id = db.select("voting_role_id", "voting", "guild_id", guild.id)
    log.debug(f"received voting_role_id: {role_id} from sql query where guild_id = {guild.id}")
    if role_id is not None:
        return guild.get_role(role_id)
    else:
        return guild.default_role




class Vote:
    def __init__(self, message, voters, embed, votes_needed, target, ctx):
        self.message = message
        self.voters = voters
        self.embed = embed
        self.users_yes = set()
        self.users_no = set()
        self.completed = False
        self.votes_needed = votes_needed
        self.target = target
        self.ctx = ctx
        

    @classmethod
    async def create(self, ctx, member):
        voter_role = get_voter_role(ctx.guild)
        voters = set([voter for voter in voter_role.members if voter.status != discord.Status.offline and not voter.bot])
        if ctx.guild.owner not in voters:
            voters.add(ctx.guild.owner)
        votes_needed = math.floor(len(voters) / 2) + 1

        embed = (discord.Embed(
            color=discord.Colour(utils.general.random_color()),
            title=f"Vote Kick:   10 minutes",
            description=f"""Voting to kick: {member.mention}
            Votes needed to win: **{votes_needed}**
            {voter_role.mention} can vote"""
            )
            .set_thumbnail(url=member.avatar_url)
            .add_field(name="Yes", value=0)
            .add_field(name="No", value=0)
        )
        message = await ctx.send(embed = embed)
        await message.add_reaction("✅")
        await message.add_reaction("❌")

        # Construc object, add it to list
        vote = Vote(message, voters, embed, votes_needed, member, ctx)
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



    async def votepass(self):
        self.embed.title="Vote Kick:   Pass"
        self.embed.color=discord.Colour(65280)
        await self.message.edit(embed = self.embed)
        await self.endvote()
        try:
            await self.ctx.guild.kick(self.target)
        except:
            await self.ctx.send(f"There was an error kicking {self.target.display_name}")


    async def votefail(self):
        self.embed.title="Vote Kick:   Fail"
        self.embed.color=discord.Colour(16711680)
        await self.message.edit(embed = self.embed)
        await self.endvote()


    async def votetime(self):
        self.embed.title="Vote Kick:   Time Exceeded"
        self.embed.color=discord.Colour(16711680)
        await self.message.edit(embed = self.embed)
        await self.endvote()


    async def endvote(self):
        await self.message.unpin()
        await self.message.clear_reactions()
        self.completed = True
        Cog.votes_in_progress.pop(self.message)


    async def update(self):
        self.embed.set_field_at(0, name="Yes", value=len(self.users_yes))
        self.embed.set_field_at(1, name="No", value=len(self.users_no))
        await self.message.edit(embed = self.embed)

        if len(self.users_yes) >= self.votes_needed:
            await self.votepass()
        elif len(self.users_no) >= self.votes_needed:
            await self.votefail()
