from discord.ext import commands
import utils.admin
import logging
import db
import pickle
log = logging.getLogger(__name__)


class Cog(commands.Cog, name='Word Blacklist'):
    blacklists = {}
    
    def __init__(self, bot):
        self.bot = bot
        log.info(f"Registered Cog: {self.qualified_name}")

    # Initalize module when bot starts
    @commands.Cog.listener()
    async def on_ready(self):
        log.info("Generating blacklist cache from database")
        await self.sync_blacklists()
        log.info("Done generating blacklist cache from database")


    

    # Commands
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
                await self.add_blacklist_word(args[1].lower(), guild_id)
                await ctx.send(f"Added `{args[1].lower()}` to blacklist")
        
        elif args[0].lower() == "remove":
            if len(args) < 2:
                return #error
            else:
                stat = await self.remove_blacklist_word(args[1], guild_id)
                if stat:
                    await ctx.send(f"Removed `{args[1].lower()}` from blacklist")
                else:
                    await ctx.send(f"Blacklist does not contain `{args[1].lower()}`")
        
        elif args[0].lower() == "show":
            message = await self.print(guild_id)
            await ctx.send(message)

        elif args[0].lower() == "clear":
            status = await self.clear_blacklist(guild_id)
            if status is None:
                await ctx.send(f"There are no blacklisted words in this server")
            else:
                await ctx.send(f"Cleared blacklisted words for `{ctx.guild.name}`")

    @blacklist.error
    async def blacklist_error(self, ctx, exception):
        await ctx.send(f"error: {exception}")


    # Event Listeners
    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.author.bot:
            blacklist = await self.get_guild_blacklist(message.guild.id)
            if blacklist is not None:
                for word in blacklist:
                    if word in message.content.lower():
                        await message.delete()
                        log.info(f"Removed message \"{message.content}\" from {message.author.display_name} in #{message.channel.name}@{message.guild.name} - contained blacklisted word: \"{word}\"")
                    
    
    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        await self.on_message(after)




    async def add_blacklist_word(self, word, guild_id):
        word_set = await self.get_or_add_guild_blacklist(guild_id)
        
        log.debug(f"Adding word '{word}' to blacklist for guild id: {guild_id}")
        word_set.add(word)

        await self.flush_cache_to_db(guild_id)



    async def remove_blacklist_word(self, word, guild_id):
        word_set = await self.get_guild_blacklist(guild_id)
        if word_set is None:
            log.debug(f"Cannot remove {word} from blacklist for guild id: {guild_id}")
        else:
            if word in word_set:
                log.debug(f"Removed word '{word}' from blacklist for guild id: {guild_id}")
                word_set.remove(word)
                await self.flush_cache_to_db(guild_id)
                return True
            else:
                log.debug(f"Word '{word}' does not exist in the blacklist for guild id: {guild_id}")
                return False



    async def clear_blacklist(self, guild_id):
        blacklist = await self.get_guild_blacklist(guild_id)
        if blacklist is None:
            return None
        else:
            blacklist.clear()
            await self.flush_cache_to_db(guild_id)
            return blacklist




    async def flush_cache_to_db(self, guild_id):
        log.debug(f"Syncing blacklist for guild id: {guild_id} to database")
        serial_blacklist = pickle.dumps(self.blacklists.get(guild_id))

        sql_data = [["guild_id", guild_id], ["blacklist_set", serial_blacklist]]
        await db.update("blacklist", sql_data)



    async def get_guild_blacklist(self, guild_id):
        if self.blacklists.get(guild_id) is None:
            log.debug(f"Cache did not contain blacklist for guild id: {guild_id}. searching database")

            serial_blacklist = await db.select("blacklist_set", "blacklist", "guild_id", guild_id)
            
            if serial_blacklist is not None:
                log.debug(f"found blacklist for guild id: {guild_id} in database. loading into cache")
                blacklist_set = pickle.loads(serial_blacklist)

                self.blacklists[guild_id] = blacklist_set
            else:
                log.debug(f"No word blacklist exists for for guild id: {guild_id}")
                return None

        return self.blacklists.get(guild_id)



    async def get_or_add_guild_blacklist(self, guild_id):
        blacklist = await self.get_guild_blacklist(guild_id)

        if blacklist is not None:
            return blacklist
        else:
            log.debug(f"Creating blacklist word set for guild id: {guild_id}")
            self.blacklists[guild_id] = set()

            log.debug(f"Adding blacklist for guild id: {guild_id} to database")
            serial_blacklist = pickle.dumps(self.blacklists.get(guild_id))

            sql_data = [["guild_id", guild_id], ["blacklist_set", serial_blacklist]]
            await db.insert("blacklist", sql_data)

            return self.blacklists.get(guild_id)



    async def remove_guild_blacklist(self, guild_id):
        if self.blacklists.get(guild_id) is None:
            log.debug(f"Guild with id: {guild_id} cannot be removed as it does not exist ")
            return

        self.blacklist.pop(guild_id)
        log.debug(f"Deleting blacklist with guild id: {guild_id} from database")
        await db.delete("blacklist", ["guild_id", guild_id])



    # sync all the guilds the bot is a member of to cache and DB
    async def sync_blacklists(self):
        member_guild_ids = set([guild.id for guild in self.bot.guilds])
        blacklist_guild_ids = self.blacklists.keys()

        log.debug("Pruning orphaned blacklists from cache")
        for blacklist_guild_id in blacklist_guild_ids:
            if blacklist_guild_id not in member_guild_ids:
                await self.remove_guild_blacklist(blacklist_guild_id)

        log.debug("Loading blacklists for member guilds into cache")
        for member_guild_id in member_guild_ids:
            await self.get_or_add_guild_blacklist(member_guild_id)



    async def print(self, guild_id):
        list = await self.get_guild_blacklist(guild_id)
        if not list:
            return "There are no blacklisted words in this server"
        else:
            return f"Blacklisted words: `{'`, `'.join(list)}`"
